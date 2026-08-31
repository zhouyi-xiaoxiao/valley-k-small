/*
 * Strict-binary64 compiled power-stream backend for the bounded F0 method.
 *
 * This file implements only generic, caller-supplied packed tensor arithmetic.
 * It knows nothing about physical controls, selectors, scientific budgets,
 * topology decisions, F0 acceptance, or resource acceptance.
 *
 * The P^T accumulation order is frozen:
 *   self;
 *   for dimension 0,1,2:
 *     incoming-forward;
 *     incoming-backward.
 *
 * Missing reflecting contributions are represented by +0.0 and are still
 * added, matching the Python batch action's masked-add semantics.  Compilation
 * is performed by the adjacent Python wrapper with contraction and unsafe
 * floating-point transformations disabled.
 */

#include <float.h>
#include <fenv.h>
#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#if FLT_RADIX != 2
#error "This backend requires a radix-two floating-point implementation."
#endif

#if DBL_MANT_DIG != 53 || DBL_MAX_EXP != 1024 || DBL_MIN_EXP != (-1021)
#error "This backend requires IEEE-754 binary64 double."
#endif

#if defined(FLT_EVAL_METHOD) && FLT_EVAL_METHOD != 0
#error "This backend requires evaluation in the declared binary64 format."
#endif

_Static_assert(sizeof(double) == 8, "binary64 must occupy exactly eight bytes");
_Static_assert(sizeof(uint64_t) == 8, "uint64_t must occupy exactly eight bytes");

#if defined(_WIN32)
#define RDF0_EXPORT __declspec(dllexport)
#else
#define RDF0_EXPORT __attribute__((visibility("default")))
#endif

enum {
    RDF0_OK = 0,
    RDF0_INVALID_ARGUMENT = 1,
    RDF0_RUNTIME_NOT_STRICT_BINARY64 = 2,
    RDF0_NONFINITE_OR_NEGATIVE_INPUT = 3,
    RDF0_SIZE_OR_ALLOCATION_FAILURE = 4,
    RDF0_NONFINITE_OR_NEGATIVE_OUTPUT = 5,
    RDF0_INVALID_TOPOLOGY = 6
};

typedef struct rdf0_runtime_probe_v1 {
    uint32_t abi_version;
    uint32_t sizeof_double;
    uint32_t flt_radix;
    uint32_t dbl_mant_dig;
    int32_t dbl_max_exp;
    int32_t dbl_min_exp;
    int32_t flt_eval_method;
    int32_t rounding_mode;
    int32_t fe_tonearest_value;
    uint32_t binary64_layout;
    uint32_t tonearest_active;
    uint32_t smallest_subnormal_preserved;
    uint32_t subnormal_arithmetic_preserved;
} rdf0_runtime_probe_v1;

static int rdf0_runtime_is_strict(rdf0_runtime_probe_v1 *probe) {
    volatile double smallest = 0x0.0000000000001p-1022;
    volatile double one = 1.0;
    volatile double half = 0.5;
    volatile double minimum_normal = 0x1.0000000000000p-1022;
    volatile double preserved = smallest * one;
    volatile double generated = minimum_normal * half;
    const int rounding = fegetround();
    const int layout_ok =
        sizeof(double) == 8 &&
        FLT_RADIX == 2 &&
        DBL_MANT_DIG == 53 &&
        DBL_MAX_EXP == 1024 &&
        DBL_MIN_EXP == -1021;
    const int tonearest_ok = rounding == FE_TONEAREST;
    const int smallest_ok = preserved == smallest && smallest != 0.0;
    const int arithmetic_ok =
        generated == 0x0.8000000000000p-1022 && generated != 0.0;

    if (probe != NULL) {
        probe->abi_version = 1U;
        probe->sizeof_double = (uint32_t)sizeof(double);
        probe->flt_radix = (uint32_t)FLT_RADIX;
        probe->dbl_mant_dig = (uint32_t)DBL_MANT_DIG;
        probe->dbl_max_exp = (int32_t)DBL_MAX_EXP;
        probe->dbl_min_exp = (int32_t)DBL_MIN_EXP;
#if defined(FLT_EVAL_METHOD)
        probe->flt_eval_method = (int32_t)FLT_EVAL_METHOD;
#else
        probe->flt_eval_method = -1;
#endif
        probe->rounding_mode = (int32_t)rounding;
        probe->fe_tonearest_value = (int32_t)FE_TONEAREST;
        probe->binary64_layout = layout_ok ? 1U : 0U;
        probe->tonearest_active = tonearest_ok ? 1U : 0U;
        probe->smallest_subnormal_preserved = smallest_ok ? 1U : 0U;
        probe->subnormal_arithmetic_preserved = arithmetic_ok ? 1U : 0U;
    }
    return layout_ok && tonearest_ok && smallest_ok && arithmetic_ok;
}

RDF0_EXPORT int rdf0_runtime_probe(
    rdf0_runtime_probe_v1 *probe
) {
    if (probe == NULL) {
        return RDF0_INVALID_ARGUMENT;
    }
    return rdf0_runtime_is_strict(probe)
        ? RDF0_OK
        : RDF0_RUNTIME_NOT_STRICT_BINARY64;
}

static int rdf0_checked_topology(
    size_t states,
    uint32_t dimensions,
    const size_t *shape,
    size_t *strides
) {
    size_t product = 1U;
    size_t running_stride = 1U;
    uint32_t dimension;

    if (
        states == 0U ||
        dimensions == 0U ||
        dimensions > 3U ||
        shape == NULL ||
        strides == NULL
    ) {
        return RDF0_INVALID_TOPOLOGY;
    }
    for (dimension = 0U; dimension < dimensions; ++dimension) {
        if (shape[dimension] < 2U || product > SIZE_MAX / shape[dimension]) {
            return RDF0_INVALID_TOPOLOGY;
        }
        product *= shape[dimension];
    }
    if (product != states || states > SIZE_MAX / sizeof(double)) {
        return RDF0_INVALID_TOPOLOGY;
    }
    for (dimension = dimensions; dimension-- > 0U;) {
        strides[dimension] = running_stride;
        if (running_stride > SIZE_MAX / shape[dimension]) {
            return RDF0_INVALID_TOPOLOGY;
        }
        running_stride *= shape[dimension];
    }
    return RDF0_OK;
}

static int rdf0_validate_nonnegative_finite(
    const double *values,
    size_t count
) {
    size_t index;
    if (values == NULL) {
        return RDF0_INVALID_ARGUMENT;
    }
    for (index = 0U; index < count; ++index) {
        if (!isfinite(values[index]) || values[index] < 0.0) {
            return RDF0_NONFINITE_OR_NEGATIVE_INPUT;
        }
    }
    return RDF0_OK;
}

static int rdf0_validate_kernel(
    size_t states,
    uint32_t dimensions,
    const size_t *shape,
    const uint8_t *periodic,
    const double *p_self,
    const double *const *p_forward,
    const double *const *p_backward,
    const double *killing,
    size_t *strides
) {
    uint32_t dimension;
    int status = rdf0_checked_topology(states, dimensions, shape, strides);
    if (status != RDF0_OK) {
        return status;
    }
    if (
        periodic == NULL ||
        p_self == NULL ||
        p_forward == NULL ||
        p_backward == NULL ||
        killing == NULL
    ) {
        return RDF0_INVALID_ARGUMENT;
    }
    status = rdf0_validate_nonnegative_finite(p_self, states);
    if (status != RDF0_OK) {
        return status;
    }
    status = rdf0_validate_nonnegative_finite(killing, states);
    if (status != RDF0_OK) {
        return status;
    }
    for (dimension = 0U; dimension < dimensions; ++dimension) {
        if (
            periodic[dimension] > 1U ||
            p_forward[dimension] == NULL ||
            p_backward[dimension] == NULL
        ) {
            return RDF0_INVALID_ARGUMENT;
        }
        status = rdf0_validate_nonnegative_finite(
            p_forward[dimension],
            shape[dimension]
        );
        if (status != RDF0_OK) {
            return status;
        }
        status = rdf0_validate_nonnegative_finite(
            p_backward[dimension],
            shape[dimension]
        );
        if (status != RDF0_OK) {
            return status;
        }
    }
    return RDF0_OK;
}

static int rdf0_apply_unchecked(
    size_t states,
    uint32_t dimensions,
    const size_t *shape,
    const size_t *strides,
    const uint8_t *periodic,
    const double *p_self,
    const double *const *p_forward,
    const double *const *p_backward,
    const double *source,
    double *destination
) {
    size_t flat;
    for (flat = 0U; flat < states; ++flat) {
        uint32_t dimension;
        double accumulator = source[flat] * p_self[flat];
        for (dimension = 0U; dimension < dimensions; ++dimension) {
            const size_t size = shape[dimension];
            const size_t stride = strides[dimension];
            const size_t coordinate = (flat / stride) % size;
            double term = 0.0;

            /* Incoming forward: source coordinate is destination - 1. */
            if (coordinate > 0U) {
                term =
                    source[flat - stride] *
                    p_forward[dimension][coordinate - 1U];
            } else if (periodic[dimension] != 0U) {
                term =
                    source[flat + (size - 1U) * stride] *
                    p_forward[dimension][size - 1U];
            }
            accumulator = accumulator + term;

            /* Incoming backward: source coordinate is destination + 1. */
            term = 0.0;
            if (coordinate + 1U < size) {
                term =
                    source[flat + stride] *
                    p_backward[dimension][coordinate + 1U];
            } else if (periodic[dimension] != 0U) {
                term =
                    source[flat - (size - 1U) * stride] *
                    p_backward[dimension][0U];
            }
            accumulator = accumulator + term;
        }
        if (!isfinite(accumulator) || accumulator < 0.0) {
            return RDF0_NONFINITE_OR_NEGATIVE_OUTPUT;
        }
        destination[flat] = accumulator;
    }
    return RDF0_OK;
}

static int rdf0_positive_mass_unchecked(
    const double *values,
    size_t states,
    double *result
) {
    size_t index;
    double total = 0.0;
    for (index = 0U; index < states; ++index) {
        total = total + values[index];
    }
    if (!isfinite(total) || total < 0.0) {
        return RDF0_NONFINITE_OR_NEGATIVE_OUTPUT;
    }
    *result = total;
    return RDF0_OK;
}

static int rdf0_positive_dot_unchecked(
    const double *left,
    const double *right,
    size_t states,
    double *result
) {
    size_t index;
    double total = 0.0;
    for (index = 0U; index < states; ++index) {
        const double term = left[index] * right[index];
        total = total + term;
    }
    if (!isfinite(total) || total < 0.0) {
        return RDF0_NONFINITE_OR_NEGATIVE_OUTPUT;
    }
    *result = total;
    return RDF0_OK;
}

RDF0_EXPORT int rdf0_apply_p_transpose(
    size_t states,
    uint32_t dimensions,
    const size_t *shape,
    const uint8_t *periodic,
    const double *p_self,
    const double *const *p_forward,
    const double *const *p_backward,
    const double *source,
    double *destination
) {
    size_t strides[3] = {0U, 0U, 0U};
    int status;
    if (!rdf0_runtime_is_strict(NULL)) {
        return RDF0_RUNTIME_NOT_STRICT_BINARY64;
    }
    if (source == NULL || destination == NULL || source == destination) {
        return RDF0_INVALID_ARGUMENT;
    }
    status = rdf0_validate_kernel(
        states,
        dimensions,
        shape,
        periodic,
        p_self,
        p_forward,
        p_backward,
        p_self,
        strides
    );
    if (status != RDF0_OK) {
        return status;
    }
    status = rdf0_validate_nonnegative_finite(source, states);
    if (status != RDF0_OK) {
        return status;
    }
    return rdf0_apply_unchecked(
        states,
        dimensions,
        shape,
        strides,
        periodic,
        p_self,
        p_forward,
        p_backward,
        source,
        destination
    );
}

RDF0_EXPORT int rdf0_positive_mass(
    size_t states,
    const double *values,
    double *result
) {
    int status;
    if (!rdf0_runtime_is_strict(NULL)) {
        return RDF0_RUNTIME_NOT_STRICT_BINARY64;
    }
    if (states == 0U || result == NULL) {
        return RDF0_INVALID_ARGUMENT;
    }
    status = rdf0_validate_nonnegative_finite(values, states);
    if (status != RDF0_OK) {
        return status;
    }
    return rdf0_positive_mass_unchecked(values, states, result);
}

RDF0_EXPORT int rdf0_positive_dot(
    size_t states,
    const double *left,
    const double *right,
    double *result
) {
    int status;
    if (!rdf0_runtime_is_strict(NULL)) {
        return RDF0_RUNTIME_NOT_STRICT_BINARY64;
    }
    if (states == 0U || result == NULL) {
        return RDF0_INVALID_ARGUMENT;
    }
    status = rdf0_validate_nonnegative_finite(left, states);
    if (status != RDF0_OK) {
        return status;
    }
    status = rdf0_validate_nonnegative_finite(right, states);
    if (status != RDF0_OK) {
        return status;
    }
    return rdf0_positive_dot_unchecked(left, right, states, result);
}

RDF0_EXPORT int rdf0_power_stream(
    size_t states,
    uint32_t dimensions,
    const size_t *shape,
    const uint8_t *periodic,
    const double *p_self,
    const double *const *p_forward,
    const double *const *p_backward,
    const double *killing,
    const double *initial,
    size_t maximum_power,
    double *mass_by_power,
    double *killing_dot_by_power,
    double *final_power
) {
    size_t strides[3] = {0U, 0U, 0U};
    double *current;
    double *following;
    size_t power;
    int status;

    if (!rdf0_runtime_is_strict(NULL)) {
        return RDF0_RUNTIME_NOT_STRICT_BINARY64;
    }
    if (
        initial == NULL ||
        mass_by_power == NULL ||
        killing_dot_by_power == NULL ||
        final_power == NULL ||
        mass_by_power == killing_dot_by_power ||
        initial == final_power
    ) {
        return RDF0_INVALID_ARGUMENT;
    }
    status = rdf0_validate_kernel(
        states,
        dimensions,
        shape,
        periodic,
        p_self,
        p_forward,
        p_backward,
        killing,
        strides
    );
    if (status != RDF0_OK) {
        return status;
    }
    status = rdf0_validate_nonnegative_finite(initial, states);
    if (status != RDF0_OK) {
        return status;
    }
    if (states > SIZE_MAX / sizeof(double)) {
        return RDF0_SIZE_OR_ALLOCATION_FAILURE;
    }
    current = (double *)malloc(states * sizeof(double));
    following = (double *)malloc(states * sizeof(double));
    if (current == NULL || following == NULL) {
        free(current);
        free(following);
        return RDF0_SIZE_OR_ALLOCATION_FAILURE;
    }
    memcpy(current, initial, states * sizeof(double));

    for (power = 0U; power <= maximum_power; ++power) {
        status = rdf0_positive_mass_unchecked(
            current,
            states,
            &mass_by_power[power]
        );
        if (status != RDF0_OK) {
            break;
        }
        status = rdf0_positive_dot_unchecked(
            killing,
            current,
            states,
            &killing_dot_by_power[power]
        );
        if (status != RDF0_OK) {
            break;
        }
        if (power < maximum_power) {
            double *swap;
            status = rdf0_apply_unchecked(
                states,
                dimensions,
                shape,
                strides,
                periodic,
                p_self,
                p_forward,
                p_backward,
                current,
                following
            );
            if (status != RDF0_OK) {
                break;
            }
            swap = current;
            current = following;
            following = swap;
        }
    }
    if (status == RDF0_OK) {
        memcpy(final_power, current, states * sizeof(double));
    }
    free(current);
    free(following);
    return status;
}

