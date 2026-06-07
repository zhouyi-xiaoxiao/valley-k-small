# Pre-shortcut formula checks

These checks compare the active TeX formulae before the shortcut section with direct finite sums or finite transition matrices.

| Check | Status | Max error | Note |
|---|---:|---:|---|
| Eq. (1)-(4) preliminary identities | PASS | `2.486900e-14` | Direct sums agree to roundoff. |
| Eq. (8) periodic propagator | PASS | `5.551115e-16` | Fourier expression matches T^t. |
| Eq. (9)-(12) first-passage time form | PASS | `2.498002e-16` | Time-domain formula matches absorbing matrix. |
| Eq. (13) corrected compact GF and Chebyshev RHS | PASS | `2.775558e-16` | Use compact upper limit N/2. |
| Eq. (13) literal printed compact upper N-1 | FAIL | `4.811867e-01` | Printed compact index is incompatible with f_k, alpha_k definitions. |
| Eq. (16) killed propagator time form | PASS | `1.642205e-15` | Matches absorbing transition submatrix. |
| Eq. (19)-(20) killed propagator GF sums | PASS | `7.993606e-15` | Modal sums match absorbing resolvent. |
| Eq. (21)-(22) Chebyshev modal sums | PASS | `5.551115e-15` | Chebyshev forms match modal sums. |
| Eq. (27)-(28) self Green functions | PASS | `3.552714e-15` | Self and antipodal forms match absorbing resolvent. |
| Line 365 first identity | PASS | `3.519744e-10` | N^2/2 identity is correct. |
| Line 365 second identity as printed | FAIL | `5.000000e-01` | Printed value is off by 1/2. |
| Line 365 second identity corrected | PASS | `1.759872e-10` | Correct value is (N^2-1)/3. |
| Line 365 third identity as printed | FAIL | `5.000000e-01` | Printed value is off by 1/2. |
| Line 365 third identity corrected | PASS | `1.759872e-10` | Correct value is -(N^2+2)/6. |

The failing Eq. (13) row is the literal compact upper limit `N-1` after `f_k` and `alpha_k` have been defined with odd-mode index `k=1,...,N/2`; using `N/2` passes.