// Method-only compiled core for transition-exact off-lattice Doi thinning.
//
// This prototype implements a constant-hazard validation channel and one
// physical broad-four-slab hazard channel.  It contains no scientific windows,
// power calculation, production-N choice, or publication decision.  Its
// purpose is to freeze and test the low-level RNG, transforms, exact free
// transition, pointwise-bounded thinning, raw-record, and deterministic
// chunk/resume contracts before any scientific protocol exists.

#include <algorithm>
#include <array>
#include <bit>
#include <cerrno>
#include <charconv>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace odt {

constexpr std::uint32_t kPhiloxM0 = 0xD2511F53U;
constexpr std::uint32_t kPhiloxM1 = 0xCD9E8D57U;
constexpr std::uint32_t kPhiloxW0 = 0x9E3779B9U;
constexpr std::uint32_t kPhiloxW1 = 0xBB67AE85U;
constexpr double kPi = 0x1.921fb54442d18p+1;
constexpr std::uint32_t kRawSchema = 2U;
constexpr std::uint32_t kEndianMarker = 0x01020304U;
constexpr std::array<unsigned char, 8> kRawMagic = {'O', 'D', 'T', 'C', 'O', 'R', '2', 0};
constexpr std::string_view kCoreBoundary = "METHOD_ONLY_OFF_LATTICE_COMPILED_CORE";

[[noreturn]] void fail(const std::string& message) { throw std::runtime_error(message); }

std::string errno_message(const std::string& prefix) {
    return prefix + ": " + std::strerror(errno);
}

std::array<std::uint32_t, 4> philox4x32_10(
    std::array<std::uint32_t, 4> counter,
    std::array<std::uint32_t, 2> key) {
    for (int round = 0; round < 10; ++round) {
        const std::uint64_t product0 =
            static_cast<std::uint64_t>(kPhiloxM0) * static_cast<std::uint64_t>(counter[0]);
        const std::uint64_t product1 =
            static_cast<std::uint64_t>(kPhiloxM1) * static_cast<std::uint64_t>(counter[2]);
        const std::uint32_t low0 = static_cast<std::uint32_t>(product0);
        const std::uint32_t high0 = static_cast<std::uint32_t>(product0 >> 32U);
        const std::uint32_t low1 = static_cast<std::uint32_t>(product1);
        const std::uint32_t high1 = static_cast<std::uint32_t>(product1 >> 32U);
        counter = {
            high1 ^ counter[1] ^ key[0],
            low1,
            high0 ^ counter[3] ^ key[1],
            low0,
        };
        if (round != 9) {
            key[0] += kPhiloxW0;
            key[1] += kPhiloxW1;
        }
    }
    return counter;
}

class PhiloxStream {
  public:
    PhiloxStream(
        const std::uint32_t master_seed,
        const std::uint32_t replicate_id,
        const std::uint64_t trajectory_id)
        : master_seed_(master_seed),
          replicate_id_(replicate_id),
          key_{static_cast<std::uint32_t>(trajectory_id),
               static_cast<std::uint32_t>(trajectory_id >> 32U)} {}

    std::uint32_t next_u32() {
        if (word_index_ == words_.size()) {
            refill();
        }
        return words_[word_index_++];
    }

    std::uint64_t next_u64() {
        const std::uint64_t high = next_u32();
        const std::uint64_t low = next_u32();
        return (high << 32U) | low;
    }

    // Exactly specified open (0,1) transform.  The upper 52 raw bits form an
    // integer j and the result is (j+1/2) 2^-52.  Every operation is exactly
    // representable in binary64 and neither endpoint can occur.
    double uniform_open() {
        const std::uint64_t mantissa = next_u64() >> 12U;
        const double value = std::ldexp(static_cast<double>(mantissa) + 0.5, -52);
        if (!(value > 0.0 && value < 1.0 && std::isfinite(value))) {
            fail("open-uniform transform escaped (0,1)");
        }
        return value;
    }

    // Inverse-CDF exponential with the fixed open-uniform transform above.
    double exponential(const double rate) {
        if (!(std::isfinite(rate) && rate > 0.0)) {
            fail("exponential rate must be finite and positive");
        }
        const double value = -std::log(uniform_open()) / rate;
        if (!(std::isfinite(value) && value > 0.0)) {
            fail("exponential transform returned an invalid increment");
        }
        return value;
    }

    // Fixed Box--Muller transform.  No std::* distribution object is used.
    double normal() {
        if (normal_cached_) {
            normal_cached_ = false;
            return cached_normal_;
        }
        const double u1 = uniform_open();
        const double u2 = uniform_open();
        const double radius = std::sqrt(-2.0 * std::log(u1));
        const double angle = 2.0 * kPi * u2;
        const double first = radius * std::cos(angle);
        cached_normal_ = radius * std::sin(angle);
        normal_cached_ = true;
        if (!(std::isfinite(first) && std::isfinite(cached_normal_))) {
            fail("Box--Muller transform returned a nonfinite normal");
        }
        return first;
    }

  private:
    void refill() {
        if (counter_exhausted_) {
            fail("trajectory Philox block counter exhausted");
        }
        words_ = philox4x32_10(
            {
                static_cast<std::uint32_t>(block_index_),
                static_cast<std::uint32_t>(block_index_ >> 32U),
                master_seed_,
                replicate_id_,
            },
            key_);
        word_index_ = 0;
        if (block_index_ == std::numeric_limits<std::uint64_t>::max()) {
            counter_exhausted_ = true;
        } else {
            ++block_index_;
        }
    }

    std::uint32_t master_seed_;
    std::uint32_t replicate_id_;
    std::array<std::uint32_t, 2> key_;
    std::uint64_t block_index_ = 0;
    bool counter_exhausted_ = false;
    std::array<std::uint32_t, 4> words_{};
    std::size_t word_index_ = 4;
    bool normal_cached_ = false;
    double cached_normal_ = 0.0;
};

class Sha256 {
  public:
    Sha256()
        : state_{
              0x6a09e667U,
              0xbb67ae85U,
              0x3c6ef372U,
              0xa54ff53aU,
              0x510e527fU,
              0x9b05688cU,
              0x1f83d9abU,
              0x5be0cd19U,
          } {}

    void update(const unsigned char* data, std::size_t size) {
        if (finalized_) {
            fail("SHA-256 update after finalization");
        }
        if (size > std::numeric_limits<std::uint64_t>::max() - total_bytes_) {
            fail("SHA-256 byte counter overflow");
        }
        total_bytes_ += static_cast<std::uint64_t>(size);
        while (size > 0) {
            const std::size_t take = std::min(size, buffer_.size() - buffer_size_);
            std::memcpy(buffer_.data() + buffer_size_, data, take);
            buffer_size_ += take;
            data += take;
            size -= take;
            if (buffer_size_ == buffer_.size()) {
                compress(buffer_.data());
                buffer_size_ = 0;
            }
        }
    }

    void update(const std::string_view value) {
        update(reinterpret_cast<const unsigned char*>(value.data()), value.size());
    }

    std::string final_hex() {
        const auto digest = final_bytes();
        std::ostringstream output;
        output << std::hex << std::setfill('0');
        for (const unsigned char byte : digest) {
            output << std::setw(2) << static_cast<unsigned int>(byte);
        }
        return output.str();
    }

  private:
    static constexpr std::array<std::uint32_t, 64> kRoundConstants = {
        0x428a2f98U, 0x71374491U, 0xb5c0fbcfU, 0xe9b5dba5U, 0x3956c25bU,
        0x59f111f1U, 0x923f82a4U, 0xab1c5ed5U, 0xd807aa98U, 0x12835b01U,
        0x243185beU, 0x550c7dc3U, 0x72be5d74U, 0x80deb1feU, 0x9bdc06a7U,
        0xc19bf174U, 0xe49b69c1U, 0xefbe4786U, 0x0fc19dc6U, 0x240ca1ccU,
        0x2de92c6fU, 0x4a7484aaU, 0x5cb0a9dcU, 0x76f988daU, 0x983e5152U,
        0xa831c66dU, 0xb00327c8U, 0xbf597fc7U, 0xc6e00bf3U, 0xd5a79147U,
        0x06ca6351U, 0x14292967U, 0x27b70a85U, 0x2e1b2138U, 0x4d2c6dfcU,
        0x53380d13U, 0x650a7354U, 0x766a0abbU, 0x81c2c92eU, 0x92722c85U,
        0xa2bfe8a1U, 0xa81a664bU, 0xc24b8b70U, 0xc76c51a3U, 0xd192e819U,
        0xd6990624U, 0xf40e3585U, 0x106aa070U, 0x19a4c116U, 0x1e376c08U,
        0x2748774cU, 0x34b0bcb5U, 0x391c0cb3U, 0x4ed8aa4aU, 0x5b9cca4fU,
        0x682e6ff3U, 0x748f82eeU, 0x78a5636fU, 0x84c87814U, 0x8cc70208U,
        0x90befffaU, 0xa4506cebU, 0xbef9a3f7U, 0xc67178f2U,
    };

    static std::uint32_t rotate_right(const std::uint32_t value, const unsigned int count) {
        return (value >> count) | (value << (32U - count));
    }

    void compress(const unsigned char* block) {
        std::array<std::uint32_t, 64> words{};
        for (std::size_t index = 0; index < 16; ++index) {
            const std::size_t offset = 4 * index;
            words[index] = (static_cast<std::uint32_t>(block[offset]) << 24U) |
                           (static_cast<std::uint32_t>(block[offset + 1]) << 16U) |
                           (static_cast<std::uint32_t>(block[offset + 2]) << 8U) |
                           static_cast<std::uint32_t>(block[offset + 3]);
        }
        for (std::size_t index = 16; index < words.size(); ++index) {
            const std::uint32_t previous15 = words[index - 15];
            const std::uint32_t previous2 = words[index - 2];
            const std::uint32_t sigma0 = rotate_right(previous15, 7) ^
                                         rotate_right(previous15, 18) ^ (previous15 >> 3U);
            const std::uint32_t sigma1 = rotate_right(previous2, 17) ^
                                         rotate_right(previous2, 19) ^ (previous2 >> 10U);
            words[index] = words[index - 16] + sigma0 + words[index - 7] + sigma1;
        }
        std::uint32_t a = state_[0];
        std::uint32_t b = state_[1];
        std::uint32_t c = state_[2];
        std::uint32_t d = state_[3];
        std::uint32_t e = state_[4];
        std::uint32_t f = state_[5];
        std::uint32_t g = state_[6];
        std::uint32_t h = state_[7];
        for (std::size_t index = 0; index < words.size(); ++index) {
            const std::uint32_t sum1 = rotate_right(e, 6) ^ rotate_right(e, 11) ^
                                       rotate_right(e, 25);
            const std::uint32_t choice = (e & f) ^ ((~e) & g);
            const std::uint32_t temporary1 =
                h + sum1 + choice + kRoundConstants[index] + words[index];
            const std::uint32_t sum0 = rotate_right(a, 2) ^ rotate_right(a, 13) ^
                                       rotate_right(a, 22);
            const std::uint32_t majority = (a & b) ^ (a & c) ^ (b & c);
            const std::uint32_t temporary2 = sum0 + majority;
            h = g;
            g = f;
            f = e;
            e = d + temporary1;
            d = c;
            c = b;
            b = a;
            a = temporary1 + temporary2;
        }
        state_[0] += a;
        state_[1] += b;
        state_[2] += c;
        state_[3] += d;
        state_[4] += e;
        state_[5] += f;
        state_[6] += g;
        state_[7] += h;
    }

    std::array<unsigned char, 32> final_bytes() {
        if (finalized_) {
            fail("SHA-256 finalized twice");
        }
        if (total_bytes_ > std::numeric_limits<std::uint64_t>::max() / 8U) {
            fail("SHA-256 bit-length counter overflow");
        }
        const std::uint64_t bit_count = total_bytes_ * 8U;
        const unsigned char one = 0x80U;
        update(&one, 1);
        const unsigned char zero = 0;
        while (buffer_size_ != 56) {
            update(&zero, 1);
        }
        std::array<unsigned char, 8> length{};
        for (std::size_t index = 0; index < length.size(); ++index) {
            length[7 - index] = static_cast<unsigned char>(bit_count >> (8U * index));
        }
        update(length.data(), length.size());
        if (buffer_size_ != 0) {
            fail("SHA-256 padding did not close a block");
        }
        finalized_ = true;
        std::array<unsigned char, 32> digest{};
        for (std::size_t index = 0; index < state_.size(); ++index) {
            digest[4 * index] = static_cast<unsigned char>(state_[index] >> 24U);
            digest[4 * index + 1] = static_cast<unsigned char>(state_[index] >> 16U);
            digest[4 * index + 2] = static_cast<unsigned char>(state_[index] >> 8U);
            digest[4 * index + 3] = static_cast<unsigned char>(state_[index]);
        }
        return digest;
    }

    std::array<std::uint32_t, 8> state_;
    std::array<unsigned char, 64> buffer_{};
    std::size_t buffer_size_ = 0;
    std::uint64_t total_bytes_ = 0;
    bool finalized_ = false;
};

std::string sha256_text(const std::string_view text) {
    Sha256 hash;
    hash.update(text);
    return hash.final_hex();
}

std::string hex_u32(const std::uint32_t value) {
    std::ostringstream output;
    output << std::hex << std::setfill('0') << std::setw(8) << value;
    return output.str();
}

std::string hex_u64(const std::uint64_t value) {
    std::ostringstream output;
    output << std::hex << std::setfill('0') << std::setw(16) << value;
    return output.str();
}

std::string double_bits_hex(const double value) {
    return hex_u64(std::bit_cast<std::uint64_t>(value));
}

struct State {
    double midpoint;
    double relative_parallel;
    double relative_perp;
};

struct FreeParameters {
    double particle_diffusion = 0.002;
    double ou_stiffness = 0.1;
    double ou_mean = 0.95;
    double transverse_width = 1.0;
    double midpoint_start = 0.14;
    double relative_parallel_start = -0.35;
    double relative_perp_start = 0.0;
    double initial_half_width = 0.02;
};

enum class HazardMode : std::uint32_t {
    constant = 0U,
    broad_four_slab = 1U,
};

constexpr double kBroadBudget = 0.01;
constexpr double kBroadLambda = 0.35;
constexpr double kContactRadius = 0.16;
constexpr double kPatchHalfWidth = 0.04;
constexpr double kBaseBumpIntegral = 0.4439938161680794;
constexpr std::array<double, 4> kPatchCentres = {0.35, 0.60, 0.75, 0.90};
static_assert(kBroadBudget > 0.0 && kBroadLambda > 0.0 && kPatchHalfWidth > 0.0);
static_assert(kBaseBumpIntegral > 0.0 && kContactRadius > 0.0 && kContactRadius < 0.5);
static_assert(kPatchCentres[1] - kPatchCentres[0] > 2.0 * kPatchHalfWidth);
static_assert(kPatchCentres[2] - kPatchCentres[1] > 2.0 * kPatchHalfWidth);
static_assert(kPatchCentres[3] - kPatchCentres[2] > 2.0 * kPatchHalfWidth);

std::string_view hazard_mode_name(const HazardMode mode) {
    switch (mode) {
        case HazardMode::constant:
            return "constant";
        case HazardMode::broad_four_slab:
            return "broad-four-slab";
    }
    fail("unknown internal hazard mode");
}

double wrap_periodic(const double value, const double period) {
    if (!(std::isfinite(value) && std::isfinite(period) && period > 0.0)) {
        fail("periodic wrapping requires finite input and a positive period");
    }
    double wrapped = value - period * std::floor((value + 0.5 * period) / period);
    if (wrapped >= 0.5 * period) {
        wrapped -= period;
    }
    if (wrapped < -0.5 * period) {
        wrapped += period;
    }
    if (!(std::isfinite(wrapped) && wrapped >= -0.5 * period && wrapped < 0.5 * period)) {
        fail("periodic wrapping escaped its half-open interval");
    }
    return wrapped;
}

double unit_bump_value(const double value) {
    if (!std::isfinite(value)) {
        fail("compact-bump argument must be finite");
    }
    if (std::abs(value) >= 1.0) {
        return 0.0;
    }
    const double result = std::exp(-1.0 / (1.0 - value * value));
    if (!(std::isfinite(result) && result >= 0.0)) {
        fail("compact-bump evaluation returned an invalid value");
    }
    return result;
}

void validate_broad_weights(const std::vector<double>& weights) {
    if (weights.size() != kPatchCentres.size()) {
        fail("broad-four-slab mode requires exactly four weights");
    }
    double total = 0.0;
    for (const double weight : weights) {
        if (!(std::isfinite(weight) && weight >= 0.0)) {
            fail("broad-four-slab weights must be finite and nonnegative");
        }
        total += weight;
    }
    if (std::abs(total - 1.0) > 2.0e-14) {
        fail("broad-four-slab weights must sum to one");
    }
}

double broad_analytic_bound(const std::vector<double>& weights) {
    validate_broad_weights(weights);
    if (!(kBaseBumpIntegral >= std::exp(-4.0 / 3.0))) {
        fail("pinned bump normalization violates the elementary lower bound");
    }
    const double maximum_weight = *std::max_element(weights.begin(), weights.end());
    const double bound = kBroadBudget * maximum_weight * std::exp(1.0 / 3.0) /
                         (kPatchHalfWidth * 1.0);
    if (!(std::isfinite(bound) && bound >= 0.0)) {
        fail("broad-four-slab analytic bound is invalid");
    }
    return bound;
}

double broad_four_slab_rate(const State& state, const std::vector<double>& weights) {
    validate_broad_weights(weights);
    if (!(std::isfinite(state.midpoint) && std::isfinite(state.relative_parallel) &&
          std::isfinite(state.relative_perp))) {
        fail("hazard state must be finite");
    }
    const double relative_perp = wrap_periodic(state.relative_perp, 1.0);
    if (std::abs(state.relative_parallel) >= kContactRadius ||
        std::abs(relative_perp) >= kContactRadius ||
        state.relative_parallel * state.relative_parallel + relative_perp * relative_perp >=
            kContactRadius * kContactRadius) {
        return 0.0;
    }
    double midpoint_profile = 0.0;
    for (std::size_t index = 0; index < kPatchCentres.size(); ++index) {
        const double left = kPatchCentres[index] - kPatchHalfWidth;
        const double right = kPatchCentres[index] + kPatchHalfWidth;
        if (!(state.midpoint > left && state.midpoint < right)) {
            continue;
        }
        const double standardized =
            (state.midpoint - kPatchCentres[index]) / kPatchHalfWidth;
        midpoint_profile +=
            weights[index] * unit_bump_value(standardized) /
            (kPatchHalfWidth * kBaseBumpIntegral);
    }
    const double rate = kBroadBudget * midpoint_profile / 1.0;
    if (!(std::isfinite(rate) && rate >= 0.0)) {
        fail("broad-four-slab hazard returned an invalid rate");
    }
    return rate;
}

double checked_killing_rate(const double rate, const double lambda_rate) {
    if (!(std::isfinite(rate) && rate >= 0.0)) {
        fail("hazard evaluation returned an invalid rate");
    }
    if (rate > lambda_rate) {
        fail("declared Lambda does not dominate an evaluated hazard");
    }
    return rate;
}

struct BumpSample {
    double value;
    std::uint32_t attempts;
};

BumpSample sample_unit_bump(PhiloxStream& rng, const std::uint32_t maximum_attempts = 512U) {
    if (maximum_attempts == 0) {
        fail("compact-bump attempt cap must be positive");
    }
    for (std::uint32_t attempt = 1; attempt <= maximum_attempts; ++attempt) {
        const double value = 2.0 * rng.uniform_open() - 1.0;
        if (!(std::abs(value) < 1.0)) {
            fail("open-uniform compact-bump proposal reached its support boundary");
        }
        const double denominator = 1.0 - value * value;
        const double acceptance = std::exp(-(value * value) / denominator);
        // Underflow to zero arbitrarily close to the open support boundary is
        // a valid fail-to-accept outcome, not a sampler failure.
        if (!(std::isfinite(acceptance) && acceptance >= 0.0 && acceptance <= 1.0)) {
            fail("compact-bump acceptance probability is invalid");
        }
        if (rng.uniform_open() < acceptance) {
            return {value, attempt};
        }
    }
    fail("compact-bump rejection cap reached; no fallback is permitted");
}

State sample_initial_state(PhiloxStream& rng, const FreeParameters& parameters) {
    const double half_width = parameters.initial_half_width;
    const State state{
        parameters.midpoint_start + half_width * sample_unit_bump(rng).value,
        parameters.relative_parallel_start + half_width * sample_unit_bump(rng).value,
        wrap_periodic(
            parameters.relative_perp_start + half_width * sample_unit_bump(rng).value,
            parameters.transverse_width),
    };
    if (!(std::isfinite(state.midpoint) && std::isfinite(state.relative_parallel) &&
          std::isfinite(state.relative_perp))) {
        fail("compact initial state is nonfinite");
    }
    return state;
}

State free_transition_with_normals(
    const State& state,
    const double delta,
    const std::array<double, 3>& normals,
    const FreeParameters& parameters) {
    if (!(std::isfinite(delta) && delta >= 0.0)) {
        fail("transition increment must be finite and nonnegative");
    }
    if (delta == 0.0) {
        return state;
    }
    const double decay = std::exp(-parameters.ou_stiffness * delta);
    const double one_minus_decay_squared =
        -std::expm1(-2.0 * parameters.ou_stiffness * delta);
    const double midpoint_variance = parameters.particle_diffusion * one_minus_decay_squared /
                                     (2.0 * parameters.ou_stiffness);
    const double relative_variance = 2.0 * parameters.particle_diffusion *
                                     one_minus_decay_squared / parameters.ou_stiffness;
    const State result{
        parameters.ou_mean + decay * (state.midpoint - parameters.ou_mean) +
            std::sqrt(midpoint_variance) * normals[0],
        decay * state.relative_parallel + std::sqrt(relative_variance) * normals[1],
        wrap_periodic(
            state.relative_perp +
                std::sqrt(4.0 * parameters.particle_diffusion * delta) * normals[2],
            parameters.transverse_width),
    };
    if (!(std::isfinite(result.midpoint) && std::isfinite(result.relative_parallel) &&
          std::isfinite(result.relative_perp))) {
        fail("exact free transition returned a nonfinite state");
    }
    return result;
}

State free_transition(
    const State& state,
    const double delta,
    PhiloxStream& rng,
    const FreeParameters& parameters) {
    return free_transition_with_normals(
        state,
        delta,
        {rng.normal(), rng.normal(), rng.normal()},
        parameters);
}

struct Record {
    std::uint64_t trajectory_id;
    double event_time;
    std::uint32_t candidate_count;
    bool reacted;
};

struct RunConfig {
    std::uint32_t master_seed;
    std::uint32_t replicate_id;
    std::uint64_t chunk_id;
    std::uint64_t id_start;
    std::uint64_t id_count;
    double horizon;
    double lambda_rate;
    HazardMode hazard_mode;
    double constant_hazard;
    std::vector<double> weights;
    std::vector<double> basin_cuts;
    std::vector<std::pair<double, double>> windows;
    std::filesystem::path raw_output;
};

void validate_config(const RunConfig& config) {
    if (config.id_count == 0) {
        fail("id_count must be positive");
    }
    if (config.id_count - 1 > std::numeric_limits<std::uint64_t>::max() - config.id_start) {
        fail("trajectory ID range overflows uint64");
    }
    if (!(std::isfinite(config.horizon) && config.horizon > 0.0 &&
          std::isfinite(config.lambda_rate) && config.lambda_rate > 0.0)) {
        fail("horizon or Lambda is invalid");
    }
    if (config.hazard_mode == HazardMode::constant) {
        if (!(std::isfinite(config.constant_hazard) && config.constant_hazard >= 0.0)) {
            fail("constant hazard is invalid");
        }
        if (config.constant_hazard > config.lambda_rate) {
            fail("declared Lambda does not dominate the constant hazard");
        }
        if (!config.weights.empty()) {
            fail("constant-hazard mode forbids broad-four-slab weights");
        }
    } else if (config.hazard_mode == HazardMode::broad_four_slab) {
        if (std::bit_cast<std::uint64_t>(config.lambda_rate) !=
            std::bit_cast<std::uint64_t>(kBroadLambda)) {
            fail("broad-four-slab mode requires the frozen Lambda=0.35");
        }
        if (std::bit_cast<std::uint64_t>(config.constant_hazard) != 0U) {
            fail("broad-four-slab mode requires the constant-hazard field to be +0");
        }
        const double bound = broad_analytic_bound(config.weights);
        if (!(bound < config.lambda_rate)) {
            fail("analytic broad-four-slab bound does not lie strictly below Lambda");
        }
    } else {
        fail("unknown internal hazard mode");
    }
    if (!config.raw_output.is_absolute()) {
        fail("raw output path must be absolute");
    }
    if (!std::filesystem::is_directory(config.raw_output.parent_path())) {
        fail("raw output parent directory does not exist");
    }
    double previous = 0.0;
    for (const double cut : config.basin_cuts) {
        if (!(std::isfinite(cut) && cut > previous && cut < config.horizon)) {
            fail("basin cuts must be finite, strictly ordered, and inside the horizon");
        }
        previous = cut;
    }
    double previous_right = -1.0;
    for (const auto& [left, right] : config.windows) {
        if (!(std::isfinite(left) && std::isfinite(right) && left >= 0.0 && left < right &&
              right <= config.horizon && left >= previous_right)) {
            fail("windows must be finite, ordered, disjoint, and inside the horizon");
        }
        previous_right = right;
    }
}

double evaluate_killing_rate(const RunConfig& config, const State& state) {
    const double rate = config.hazard_mode == HazardMode::constant
                            ? config.constant_hazard
                            : broad_four_slab_rate(state, config.weights);
    return checked_killing_rate(rate, config.lambda_rate);
}

Record simulate_trajectory(
    const RunConfig& config,
    const std::uint64_t trajectory_id,
    const FreeParameters& parameters) {
    PhiloxStream rng(config.master_seed, config.replicate_id, trajectory_id);
    State state = sample_initial_state(rng, parameters);
    double time = 0.0;
    std::uint32_t candidates = 0;
    while (true) {
        const double delta = rng.exponential(config.lambda_rate);
        if (delta > config.horizon - time) {
            return {trajectory_id, std::numeric_limits<double>::infinity(), candidates, false};
        }
        const double candidate_time = time + delta;
        if (!(candidate_time > time && std::isfinite(candidate_time))) {
            fail("candidate time failed to advance monotonically");
        }
        state = free_transition(state, delta, rng, parameters);
        time = candidate_time;
        if (candidates == std::numeric_limits<std::uint32_t>::max()) {
            fail("per-trajectory candidate counter overflow");
        }
        ++candidates;
        // The pointwise check is deliberately repeated at every evaluated
        // candidate.  No clipping to Lambda is permitted.
        const double killing_rate = evaluate_killing_rate(config, state);
        if (rng.uniform_open() < killing_rate / config.lambda_rate) {
            return {trajectory_id, time, candidates, true};
        }
    }
}

class AtomicRawWriter {
  public:
    explicit AtomicRawWriter(const std::filesystem::path& final_path)
        : final_path_(final_path),
          stage_path_(final_path.string() + ".partial." + std::to_string(::getpid())) {
        struct stat metadata {};
        if (::lstat(final_path_.c_str(), &metadata) == 0) {
            fail("raw output already exists; overwrite is forbidden");
        }
        if (errno != ENOENT) {
            fail(errno_message("cannot inspect raw output"));
        }
        descriptor_ = ::open(stage_path_.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0600);
        if (descriptor_ < 0) {
            fail(errno_message("cannot create private raw staging file"));
        }
    }

    AtomicRawWriter(const AtomicRawWriter&) = delete;
    AtomicRawWriter& operator=(const AtomicRawWriter&) = delete;

    ~AtomicRawWriter() {
        if (descriptor_ >= 0) {
            ::close(descriptor_);
        }
        if (!committed_) {
            ::unlink(stage_path_.c_str());
        }
    }

    void write(const unsigned char* data, const std::size_t size) {
        if (descriptor_ < 0 || committed_) {
            fail("raw writer is not open");
        }
        std::size_t offset = 0;
        while (offset < size) {
            const ssize_t written =
                ::write(descriptor_, data + offset, static_cast<std::size_t>(size - offset));
            if (written < 0) {
                if (errno == EINTR) {
                    continue;
                }
                fail(errno_message("raw staging write failed"));
            }
            if (written == 0) {
                fail("raw staging write made no progress");
            }
            offset += static_cast<std::size_t>(written);
        }
        hash_.update(data, size);
        if (size > std::numeric_limits<std::uint64_t>::max() - byte_count_) {
            fail("raw byte counter overflow");
        }
        byte_count_ += static_cast<std::uint64_t>(size);
    }

    template <typename Integer>
    void write_little_endian(const Integer value) {
        static_assert(std::is_unsigned_v<Integer>);
        std::array<unsigned char, sizeof(Integer)> bytes{};
        for (std::size_t index = 0; index < bytes.size(); ++index) {
            bytes[index] = static_cast<unsigned char>(value >> (8U * index));
        }
        write(bytes.data(), bytes.size());
    }

    std::pair<std::string, std::uint64_t> commit() {
        if (::fsync(descriptor_) != 0) {
            fail(errno_message("raw staging fsync failed"));
        }
        if (::close(descriptor_) != 0) {
            descriptor_ = -1;
            fail(errno_message("raw staging close failed"));
        }
        descriptor_ = -1;
        const std::string digest = hash_.final_hex();
        if (::link(stage_path_.c_str(), final_path_.c_str()) != 0) {
            fail(errno_message("atomic no-replace raw install failed"));
        }
        linked_ = true;
        if (::unlink(stage_path_.c_str()) != 0) {
            ::unlink(final_path_.c_str());
            fail(errno_message("raw staging unlink failed"));
        }
        linked_ = false;
        const int directory = ::open(final_path_.parent_path().c_str(), O_RDONLY | O_DIRECTORY);
        if (directory < 0) {
            ::unlink(final_path_.c_str());
            fail(errno_message("raw output directory open failed"));
        }
        const int sync_result = ::fsync(directory);
        const int close_result = ::close(directory);
        if (sync_result != 0 || close_result != 0) {
            ::unlink(final_path_.c_str());
            fail("raw output directory synchronization failed");
        }
        committed_ = true;
        return {digest, byte_count_};
    }

  private:
    std::filesystem::path final_path_;
    std::filesystem::path stage_path_;
    int descriptor_ = -1;
    bool linked_ = false;
    bool committed_ = false;
    Sha256 hash_;
    std::uint64_t byte_count_ = 0;
};

struct ChunkSummary {
    std::string raw_sha256;
    std::uint64_t raw_byte_count;
    std::uint64_t reaction_count;
    std::uint64_t censored_count;
    std::uint64_t candidate_count_sum;
    std::uint32_t candidate_count_maximum;
    std::vector<std::uint64_t> basin_counts;
    std::vector<std::uint64_t> window_counts;
};

void write_raw_header(AtomicRawWriter& writer, const RunConfig& config) {
    writer.write(kRawMagic.data(), kRawMagic.size());
    writer.write_little_endian(kEndianMarker);
    writer.write_little_endian(kRawSchema);
    writer.write_little_endian(config.master_seed);
    writer.write_little_endian(config.replicate_id);
    writer.write_little_endian(config.chunk_id);
    writer.write_little_endian(config.id_start);
    writer.write_little_endian(config.id_count);
    writer.write_little_endian(std::bit_cast<std::uint64_t>(config.horizon));
    writer.write_little_endian(std::bit_cast<std::uint64_t>(config.lambda_rate));
    writer.write_little_endian(std::bit_cast<std::uint64_t>(config.constant_hazard));
    if (config.weights.size() > std::numeric_limits<std::uint32_t>::max() ||
        config.basin_cuts.size() > std::numeric_limits<std::uint32_t>::max() ||
        config.windows.size() > std::numeric_limits<std::uint32_t>::max()) {
        fail("count specification is too large for the raw format");
    }
    writer.write_little_endian(static_cast<std::uint32_t>(config.hazard_mode));
    writer.write_little_endian(static_cast<std::uint32_t>(config.weights.size()));
    writer.write_little_endian(static_cast<std::uint32_t>(config.basin_cuts.size()));
    writer.write_little_endian(static_cast<std::uint32_t>(config.windows.size()));
    for (const double weight : config.weights) {
        writer.write_little_endian(std::bit_cast<std::uint64_t>(weight));
    }
    for (const double cut : config.basin_cuts) {
        writer.write_little_endian(std::bit_cast<std::uint64_t>(cut));
    }
    for (const auto& [left, right] : config.windows) {
        writer.write_little_endian(std::bit_cast<std::uint64_t>(left));
        writer.write_little_endian(std::bit_cast<std::uint64_t>(right));
    }
}

void write_raw_record(AtomicRawWriter& writer, const Record& record) {
    writer.write_little_endian(record.trajectory_id);
    writer.write_little_endian(std::bit_cast<std::uint64_t>(record.event_time));
    writer.write_little_endian(record.candidate_count);
    writer.write_little_endian(static_cast<std::uint32_t>(record.reacted ? 1U : 0U));
}

ChunkSummary run_chunk(const RunConfig& config) {
    validate_config(config);
    AtomicRawWriter writer(config.raw_output);
    write_raw_header(writer, config);
    ChunkSummary summary{
        "",
        0,
        0,
        0,
        0,
        0,
        std::vector<std::uint64_t>(config.basin_cuts.size() + 1, 0),
        std::vector<std::uint64_t>(config.windows.size(), 0),
    };
    const FreeParameters parameters;
    for (std::uint64_t offset = 0; offset < config.id_count; ++offset) {
        const std::uint64_t trajectory_id = config.id_start + offset;
        const Record record = simulate_trajectory(config, trajectory_id, parameters);
        write_raw_record(writer, record);
        if (record.candidate_count >
            std::numeric_limits<std::uint64_t>::max() - summary.candidate_count_sum) {
            fail("chunk candidate-count sum overflow");
        }
        summary.candidate_count_sum += record.candidate_count;
        summary.candidate_count_maximum =
            std::max(summary.candidate_count_maximum, record.candidate_count);
        if (record.reacted) {
            ++summary.reaction_count;
            const auto basin = std::upper_bound(
                config.basin_cuts.begin(), config.basin_cuts.end(), record.event_time);
            ++summary.basin_counts[static_cast<std::size_t>(basin - config.basin_cuts.begin())];
            for (std::size_t index = 0; index < config.windows.size(); ++index) {
                const auto& [left, right] = config.windows[index];
                if (record.event_time >= left && record.event_time < right) {
                    ++summary.window_counts[index];
                }
            }
        } else {
            ++summary.censored_count;
        }
    }
    const std::uint64_t basin_sum = [&summary]() {
        std::uint64_t total = 0;
        for (const std::uint64_t count : summary.basin_counts) {
            total += count;
        }
        return total;
    }();
    if (summary.reaction_count + summary.censored_count != config.id_count ||
        basin_sum != summary.reaction_count) {
        fail("integer event/censor/basin closure failed");
    }
    auto [digest, byte_count] = writer.commit();
    summary.raw_sha256 = std::move(digest);
    summary.raw_byte_count = byte_count;
    return summary;
}

std::string chunk_summary_json(const RunConfig& config, const ChunkSummary& summary) {
    std::ostringstream output;
    output << '{'
           << "\"chunk_id\":" << config.chunk_id << ','
           << "\"claim_flags\":{"
           << "\"independent_solver_verified\":false,"
           << "\"modality_confirmed\":false,"
           << "\"production_run_authorized\":false,"
           << "\"scientific_estimand_frozen\":false,"
           << "\"scientific_event_ensemble\":false},"
           << "\"constant_hazard_bits\":\"" << double_bits_hex(config.constant_hazard)
           << "\","
           << "\"core_boundary\":\"" << kCoreBoundary << "\","
           << "\"hazard_mode\":\"" << hazard_mode_name(config.hazard_mode) << "\","
           << "\"horizon_bits\":\"" << double_bits_hex(config.horizon) << "\","
           << "\"id_count\":" << config.id_count << ','
           << "\"id_start\":" << config.id_start << ','
           << "\"lambda_bits\":\"" << double_bits_hex(config.lambda_rate) << "\","
           << "\"master_seed\":" << config.master_seed << ','
           << "\"raw_byte_count\":" << summary.raw_byte_count << ','
           << "\"raw_record_bytes\":24,"
           << "\"raw_schema\":2,"
           << "\"raw_sha256\":\"" << summary.raw_sha256 << "\","
           << "\"replicate_id\":" << config.replicate_id << ','
           << "\"schema_version\":2,"
           << "\"stage\":\"METHOD_ONLY_OFF_LATTICE_RAW_CHUNK_COMPLETE\","
           << "\"statistical_estimates_released\":false,"
           << "\"weight_bits\":[";
    for (std::size_t index = 0; index < config.weights.size(); ++index) {
        if (index != 0) {
            output << ',';
        }
        output << '\"' << double_bits_hex(config.weights[index]) << '\"';
    }
    output << ']'
           << "}\n";
    return output.str();
}

std::string fixtures_json() {
    const auto zero = philox4x32_10({0, 0, 0, 0}, {0, 0});
    constexpr std::uint32_t master = 0x12345678U;
    constexpr std::uint32_t replicate = 0x9abcdef0U;
    constexpr std::uint64_t trajectory = 0x0123456789abcdefULL;
    std::array<std::array<std::uint32_t, 4>, 4> blocks{};
    for (std::uint64_t block = 0; block < blocks.size(); ++block) {
        blocks[block] = philox4x32_10(
            {
                static_cast<std::uint32_t>(block),
                static_cast<std::uint32_t>(block >> 32U),
                master,
                replicate,
            },
            {
                static_cast<std::uint32_t>(trajectory),
                static_cast<std::uint32_t>(trajectory >> 32U),
            });
    }
    PhiloxStream raw_stream(master, replicate, trajectory);
    std::array<std::uint32_t, 12> raw_words{};
    for (auto& word : raw_words) {
        word = raw_stream.next_u32();
    }
    PhiloxStream uniform_stream(master, replicate, trajectory);
    std::array<double, 4> uniforms{};
    for (double& value : uniforms) {
        value = uniform_stream.uniform_open();
    }
    PhiloxStream exponential_stream(master, replicate, trajectory);
    std::array<double, 4> exponentials{};
    for (double& value : exponentials) {
        value = exponential_stream.exponential(0.13);
    }
    PhiloxStream normal_stream(master, replicate, trajectory);
    std::array<double, 6> normals{};
    for (double& value : normals) {
        value = normal_stream.normal();
    }
    PhiloxStream bump_stream(master, replicate, trajectory);
    std::array<BumpSample, 3> bumps{};
    for (auto& sample : bumps) {
        sample = sample_unit_bump(bump_stream);
    }
    const State transition = free_transition_with_normals(
        {0.2, -0.3, 0.49},
        1.7,
        {0.25, -0.5, 1.25},
        FreeParameters{});
    const std::vector<double> hazard_weights = {0.4, 0.3, 0.2, 0.1};
    const std::vector<double> unit_weight = {1.0, 0.0, 0.0, 0.0};
    const double simplex_bound = broad_analytic_bound(unit_weight);
    const double fixture_bound = broad_analytic_bound(hazard_weights);
    std::array<double, 4> all_center_rates{};
    for (std::size_t index = 0; index < all_center_rates.size(); ++index) {
        all_center_rates[index] = checked_killing_rate(
            broad_four_slab_rate({kPatchCentres[index], 0.0, 0.0}, hazard_weights),
            kBroadLambda);
    }
    const double center_rate = all_center_rates[0];
    const double contact_inside_rate = checked_killing_rate(
        broad_four_slab_rate(
            {kPatchCentres[0], std::nextafter(kContactRadius, 0.0), 0.0},
            hazard_weights),
        kBroadLambda);
    const double contact_edge_rate = checked_killing_rate(
        broad_four_slab_rate({kPatchCentres[0], kContactRadius, 0.0}, hazard_weights),
        kBroadLambda);
    const double contact_outside_rate = checked_killing_rate(
        broad_four_slab_rate(
            {kPatchCentres[0], std::nextafter(kContactRadius, 1.0), 0.0},
            hazard_weights),
        kBroadLambda);
    const double minimum_image_rate = checked_killing_rate(
        broad_four_slab_rate({kPatchCentres[0], 0.0, 0.99}, hazard_weights),
        kBroadLambda);
    const double minimum_image_reference_rate = checked_killing_rate(
        broad_four_slab_rate({kPatchCentres[0], 0.0, -0.01}, hazard_weights),
        kBroadLambda);
    const double bump_edge_rate = checked_killing_rate(
        broad_four_slab_rate(
            {kPatchCentres[0] + kPatchHalfWidth, 0.0, 0.0}, hazard_weights),
        kBroadLambda);
    const double bump_near_edge_rate = checked_killing_rate(
        broad_four_slab_rate(
            {kPatchCentres[0] + 0.75 * kPatchHalfWidth, 0.0, 0.0},
            hazard_weights),
        kBroadLambda);
    const double zero_rate = checked_killing_rate(
        broad_four_slab_rate({0.0, 0.0, 0.0}, hazard_weights), kBroadLambda);
    const double near_lambda_guard = checked_killing_rate(
        std::nextafter(kBroadLambda, 0.0), kBroadLambda);

    auto emit_u32_hex_array = [](std::ostringstream& output, const auto& values) {
        output << '[';
        for (std::size_t index = 0; index < values.size(); ++index) {
            if (index != 0) {
                output << ',';
            }
            output << '\"' << hex_u32(values[index]) << '\"';
        }
        output << ']';
    };
    auto emit_double_bits_array = [](std::ostringstream& output, const auto& values) {
        output << '[';
        for (std::size_t index = 0; index < values.size(); ++index) {
            if (index != 0) {
                output << ',';
            }
            output << '\"' << double_bits_hex(values[index]) << '\"';
        }
        output << ']';
    };

    std::ostringstream output;
    output << '{' << "\"bump_samples\":[";
    for (std::size_t index = 0; index < bumps.size(); ++index) {
        if (index != 0) {
            output << ',';
        }
        output << "{\"attempts\":" << bumps[index].attempts << ",\"value_bits\":\""
               << double_bits_hex(bumps[index].value) << "\"}";
    }
    output << "],\"exponential_0p13_bits\":";
    emit_double_bits_array(output, exponentials);
    output << ",\"fixed_transition_bits\":[\"" << double_bits_hex(transition.midpoint)
           << "\",\"" << double_bits_hex(transition.relative_parallel) << "\",\""
           << double_bits_hex(transition.relative_perp) << "\"],"
           << "\"hazard_fixtures\":{\"all_center_rate_bits\":";
    emit_double_bits_array(output, all_center_rates);
    output << ",\"analytic_fixture_bound_bits\":\"" << double_bits_hex(fixture_bound)
           << "\","
           << "\"analytic_simplex_bound_bits\":\"" << double_bits_hex(simplex_bound)
           << "\","
           << "\"broad_budget_bits\":\"" << double_bits_hex(kBroadBudget) << "\","
           << "\"broad_lambda_bits\":\"" << double_bits_hex(kBroadLambda) << "\","
           << "\"bump_edge_rate_bits\":\"" << double_bits_hex(bump_edge_rate) << "\","
           << "\"bump_near_edge_rate_bits\":\"" << double_bits_hex(bump_near_edge_rate)
           << "\","
           << "\"center_rate_bits\":\"" << double_bits_hex(center_rate) << "\","
           << "\"contact_edge_rate_bits\":\"" << double_bits_hex(contact_edge_rate)
           << "\","
           << "\"contact_inside_rate_bits\":\"" << double_bits_hex(contact_inside_rate)
           << "\","
           << "\"contact_outside_rate_bits\":\"" << double_bits_hex(contact_outside_rate)
           << "\","
           << "\"minimum_image_equal\":"
           << (double_bits_hex(minimum_image_rate) ==
                       double_bits_hex(minimum_image_reference_rate)
                   ? "true"
                   : "false")
           << ','
           << "\"minimum_image_rate_bits\":\"" << double_bits_hex(minimum_image_rate)
           << "\","
           << "\"near_lambda_guard_bits\":\"" << double_bits_hex(near_lambda_guard)
           << "\","
           << "\"normalization_bits\":\"" << double_bits_hex(kBaseBumpIntegral)
           << "\","
           << "\"simplex_margin_bits\":\""
           << double_bits_hex(kBroadLambda - simplex_bound) << "\","
           << "\"zero_rate_bits\":\"" << double_bits_hex(zero_rate) << "\"},"
           << "\"normal_bits\":";
    emit_double_bits_array(output, normals);
    output << ",\"philox_blocks\":[";
    for (std::size_t index = 0; index < blocks.size(); ++index) {
        if (index != 0) {
            output << ',';
        }
        emit_u32_hex_array(output, blocks[index]);
    }
    output << "],\"philox_known_zero_vector\":";
    emit_u32_hex_array(output, zero);
    output << ",\"core_boundary\":\"" << kCoreBoundary << "\""
           << ",\"raw_words\":";
    emit_u32_hex_array(output, raw_words);
    output << ",\"schema_version\":2,\"sha256_abc\":\"" << sha256_text("abc")
           << "\",\"uniform_open_bits\":";
    emit_double_bits_array(output, uniforms);
    output << "}\n";
    return output.str();
}

std::uint64_t parse_u64(const std::string& text, const std::string& label) {
    std::uint64_t value = 0;
    const char* begin = text.data();
    const char* end = begin + text.size();
    const auto [pointer, error] = std::from_chars(begin, end, value, 10);
    if (error != std::errc{} || pointer != end) {
        fail(label + " must be an unsigned decimal integer");
    }
    return value;
}

std::uint32_t parse_u32(const std::string& text, const std::string& label) {
    const std::uint64_t value = parse_u64(text, label);
    if (value > std::numeric_limits<std::uint32_t>::max()) {
        fail(label + " exceeds uint32");
    }
    return static_cast<std::uint32_t>(value);
}

double parse_double(const std::string& text, const std::string& label) {
    char* end = nullptr;
    errno = 0;
    const double value = std::strtod(text.c_str(), &end);
    if (errno != 0 || end != text.c_str() + text.size() || !std::isfinite(value)) {
        fail(label + " must be one finite decimal binary64 value");
    }
    return value;
}

std::vector<std::string> split(const std::string& text, const char delimiter) {
    std::vector<std::string> values;
    std::size_t start = 0;
    while (start <= text.size()) {
        const std::size_t position = text.find(delimiter, start);
        values.push_back(text.substr(start, position - start));
        if (position == std::string::npos) {
            break;
        }
        start = position + 1;
    }
    return values;
}

std::vector<double> parse_cuts(const std::string& text) {
    if (text.empty()) {
        return {};
    }
    std::vector<double> values;
    for (const std::string& item : split(text, ',')) {
        values.push_back(parse_double(item, "basin cut"));
    }
    return values;
}

std::vector<double> parse_weights(const std::string& text) {
    if (text.empty()) {
        return {};
    }
    std::vector<double> values;
    for (const std::string& item : split(text, ',')) {
        values.push_back(parse_double(item, "hazard weight"));
    }
    return values;
}

HazardMode parse_hazard_mode(const std::string& text) {
    if (text == "constant") {
        return HazardMode::constant;
    }
    if (text == "broad-four-slab") {
        return HazardMode::broad_four_slab;
    }
    fail("hazard mode must be constant or broad-four-slab");
}

std::vector<std::pair<double, double>> parse_windows(const std::string& text) {
    if (text.empty()) {
        return {};
    }
    std::vector<std::pair<double, double>> values;
    for (const std::string& item : split(text, ',')) {
        const auto endpoints = split(item, ':');
        if (endpoints.size() != 2) {
            fail("each window must have left:right form");
        }
        values.emplace_back(
            parse_double(endpoints[0], "window left endpoint"),
            parse_double(endpoints[1], "window right endpoint"));
    }
    return values;
}

std::map<std::string, std::string> parse_options(const int argc, char** argv, const int start) {
    std::map<std::string, std::string> options;
    for (int index = start; index < argc; index += 2) {
        if (index + 1 >= argc) {
            fail("every option requires one value");
        }
        const std::string key(argv[index]);
        if (!key.starts_with("--") || !options.emplace(key, argv[index + 1]).second) {
            fail("options must be unique --name value pairs");
        }
    }
    return options;
}

std::string take_option(std::map<std::string, std::string>& options, const std::string& key) {
    const auto found = options.find(key);
    if (found == options.end()) {
        fail("missing required option " + key);
    }
    std::string value = found->second;
    options.erase(found);
    return value;
}

RunConfig parse_run_config(const int argc, char** argv) {
    auto options = parse_options(argc, argv, 2);
    RunConfig config{
        parse_u32(take_option(options, "--master-seed"), "master seed"),
        parse_u32(take_option(options, "--replicate-id"), "replicate ID"),
        parse_u64(take_option(options, "--chunk-id"), "chunk ID"),
        parse_u64(take_option(options, "--id-start"), "ID start"),
        parse_u64(take_option(options, "--id-count"), "ID count"),
        parse_double(take_option(options, "--horizon"), "horizon"),
        parse_double(take_option(options, "--lambda"), "Lambda"),
        parse_hazard_mode(take_option(options, "--hazard-mode")),
        parse_double(take_option(options, "--constant-hazard"), "constant hazard"),
        parse_weights(take_option(options, "--weights")),
        parse_cuts(take_option(options, "--basin-cuts")),
        parse_windows(take_option(options, "--windows")),
        std::filesystem::path(take_option(options, "--raw-output")),
    };
    if (!options.empty()) {
        fail("unknown option " + options.begin()->first);
    }
    return config;
}

}  // namespace odt

int main(int argc, char** argv) {
    try {
        if (argc < 2) {
            odt::fail(
                "expected subcommand fixtures, hazard-bound-violation-fixture, or run-chunk");
        }
        const std::string command(argv[1]);
        if (command == "fixtures") {
            if (argc != 2) {
                odt::fail("fixtures accepts no options");
            }
            std::cout << odt::fixtures_json();
            return 0;
        }
        if (command == "hazard-bound-violation-fixture") {
            if (argc != 2) {
                odt::fail("hazard-bound-violation-fixture accepts no options");
            }
            static_cast<void>(odt::checked_killing_rate(
                std::nextafter(odt::kBroadLambda, std::numeric_limits<double>::infinity()),
                odt::kBroadLambda));
            odt::fail("hazard-bound-violation-fixture unexpectedly returned");
        }
        if (command == "run-chunk") {
            const odt::RunConfig config = odt::parse_run_config(argc, argv);
            const odt::ChunkSummary summary = odt::run_chunk(config);
            std::cout << odt::chunk_summary_json(config, summary);
            return 0;
        }
        odt::fail("unknown subcommand");
    } catch (const std::exception& error) {
        std::cerr << "HOLD: " << error.what() << '\n';
        return 2;
    }
}
