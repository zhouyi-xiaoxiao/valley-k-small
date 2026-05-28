# Encounter Green Formula Comparison

## Literature Formula and Conventions

The comparison uses the finite-state Green/renewal identity behind the
multi-target first-passage formalism.  For an unabsorbed row-stochastic
transition matrix `P` and target set `E`,

```text
G(z) = (I - z P)^(-1)
G[start, E] = F[start, E](z) G[E, E]
F[start, E](z) = G[start, E] G[E, E]^(-1)
F_E(z) = sum_{e in E} F[start, e](z).
```

This is the multi-target version of the single-target renewal ratio
`F_{a->b}(z)=G[a,b](z)/G[b,b](z)`.  The determinant expressions in the
literature are algebraically equivalent to solving this target-target
linear system for the fully absorbing case.

Convention match used in this numerical comparison:

- Boundary: reflecting finite interval with attempted-outside-stays.
- Update: discrete-time synchronous product chain for two independent walkers.
- Laziness: walker `i` has stay probability `1-Q_i` in the interior, plus reflected attempted moves at endpoints.
- Encounter/targets: `E={(k,k): 0<=k<L}` in the joint state space.
- Mobility: `Q1=2*q0*rho/(1+rho)` and `Q2=2*q0/(1+rho)`.

The published periodic/resetting first-transmission example is not claimed
to be identical to this report's reflecting fixed-total-mobility scan. The
equality claim here is only for the general Green/renewal formula evaluated
with the same unabsorbed reflecting lazy product propagator used by this
codebase.

## Absorbing-Chain Formula

Let `M=P[T,T]` be the transient-transient block, `R=P[T,E]` the
transient-to-encounter block, and `alpha` the row vector concentrated at
the non-diagonal start. The existing absorbing-chain generating function is

```text
F_E(z) = z alpha (I - z M)^(-1) R 1.
```

The channel-resolved absorbing formula is `z alpha (I-zM)^(-1) R`; summing
over diagonal targets gives the total encounter generating function.

## Numerical Result

- Cases: 2
- z values per case: 4
- max total absolute error: 1.388e-17
- max channel absolute error: 5.204e-18
- Output CSV: `data/green_formula_comparison.csv`
- Output JSON: `outputs/green_formula_comparison_summary.json`

| case_id | z | abs_error | max_channel_abs_error |
|---|---:|---:|---:|
| L5_edge_to_edge_rho2 | 0.1 | 3.388e-21 | 1.694e-21 |
| L5_edge_to_edge_rho2 | 0.4 | 4.337e-19 | 3.253e-19 |
| L5_edge_to_edge_rho2 | 0.75 | 1.388e-17 | 5.204e-18 |
| L5_edge_to_edge_rho2 | 0.5+0.2i | 2.743e-18 | 1.189e-18 |
| L7_inner_pair_rho1 | 0.1 | 3.388e-21 | 1.694e-21 |
| L7_inner_pair_rho1 | 0.4 | 4.337e-19 | 2.168e-19 |
| L7_inner_pair_rho1 | 0.75 | 0.000e+00 | 1.735e-18 |
| L7_inner_pair_rho1 | 0.5+0.2i | 4.470e-19 | 2.881e-19 |

## Limitations

- Source checked: L. Giuggioli, S. Sarvaharman, D. Das, D. Marris, and
  T. Kay, "Multi-target search in bounded and heterogeneous environments: a
  lattice random walk perspective", arXiv:2311.00464v2.  The relevant pieces
  are the single-target renewal ratio, the multi-target any-target formula,
  and the statement that encounter/transmission can be represented as first
  absorption at the product-space meeting sites.
- This is a small `L=5`/`L=7` z-domain check, not a large scan.
- It validates exact formula equivalence only under the matched conventions above.
- It does not claim equality to closed forms whose published examples assume periodic boundaries, resetting, partial transmission, or different mobility definitions.
