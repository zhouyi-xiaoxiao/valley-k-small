# Independent audit: long-time tail of the antipodal-shortcut first passage

Model: lazy ring N=2L, stay 1-q, hop q/2; absorbing v=0; directed shortcut
u=L->v with weight beta(1-q) moved from the self-loop. All checks deterministic.

## A. Collected closed form vs exact finite chain (exact rationals)
  N=10 q=2/3 beta=4/7: max |exact - closed form| over n0, t<=60 : 4.38e-62
  N=8 q=1/2 beta=1/3: max |exact - closed form| over n0, t<=60 : 1.94e-62
  N=14 q=3/5 beta=9/10: max |exact - closed form| over n0, t<=60 : 1.94e-61

## B. Spectrum of the transient block (symmetric => diagonalizable)
  max |T - T^t| = 0.0   (transient block is exactly symmetric)
  spectrum == {roots of D} U {gamma_r} : max err = 5.45e-61
  minimal eigenvalue gap = 0.0656 (all simple; no Jordan block possible)
  min distance spectrum <-> alpha_l = 0.0291  (alpha_l NOT an eigenvalue)

## C. Tail diagnostics (mp dps=60)
  alpha_1 = 0.967371010863, s_1 = 0.938305915619, gamma_1 = 0.87267799625
  t=   50  F(t)/F(t-1)=0.93830590412972   F/(B1 s1^(t-1))=1.000000034   F/(t alpha1^(t-1))=0.0003151
  t=  200  F(t)/F(t-1)=0.938305915618549   F/(B1 s1^(t-1))=1.0   F/(t alpha1^(t-1))=8.111e-7
  t=  800  F(t)/F(t-1)=0.938305915618549   F/(B1 s1^(t-1))=1.0   F/(t alpha1^(t-1))=2.28e-15
  t= 2000  F(t)/F(t-1)=0.938305915618549   F/(B1 s1^(t-1))=1.0   F/(t alpha1^(t-1))=1.152e-31
  t= 2999  F(t)/F(t-1)=0.938305915618549   F/(B1 s1^(t-1))=1.0   F/(t alpha1^(t-1))=4.47e-45
  => geometric decay at s_1; the t*alpha_1^t normalisation diverges from any constant: ratio -> 0

## D. Cancellation identities and five-group mode bookkeeping
  (i)  sum_j c_j/(s_j-alpha_l) - h0 : max |.| over l = 3.89e-61   [H~(1/alpha_l)=0]
  (i') sum_j c_j/(gamma_r-s_j) : max |.| = 1.49e-61   [H~(1/gamma_r)=h0]
  (ii) T_(L-rho)(eta_l)U_(L-1)(eta_l)-U_(rho-1)(eta_l) : max |.| = 3.11e-60
  five-group totals (N=10, q=2/3, beta=4/7, n0=3):
    coefficient of (t-1)*alpha_l^(t-2): max |.| = 3.57e-63  -> 0
    coefficient of alpha_l^(t-1)      : max |.| = 2.64e-61  -> 0
    coefficient of gamma_r^(t-1)      : max |.| = 4.74e-62  -> 0
    coefficient of s_j^(t-1) - B_rho_j: max |.| = 1.75e-61  -> B matches
    G1_r(n0=3, u=L, v=0): max |.| = 1.24e-61  (gamma modes absent at antipodal u)
  (i) across N=8..20, q=0.2..0.9, beta=0.01..1: max deviation = 1.14e-59 (identity, not tuning)

## E. Luca's Eq. (41) evaluated literally vs the exact PMF
  as written (his c_k, his signs, baseline f(n0,u)):   max|err| = 256.0, sum_t F = -7866.31 (should -> 1)
  sign repaired + baseline f(n0,v), his c_k:           max|err| = 256.0
  sign repaired + baseline f(n0,v) + true residues c_j: max|err| = 0.0381
    (remaining error = the H(0) boundary term + gamma-pairing of the g-modes;
     his kernels use (s^t-x^t)/(s(s-x)), i.e. they extend H(t)=sum c_k s_k^(t-1) down to t=0)
  H(0) true = beta(1-q)/q = 0.285714285714
  H(0) implied by extending the pole sum = sum_k c_k/s_k = 0.103896103896
  mismatch = 0.181818181818  (nonzero: the spurious t*alpha^t source)
  his t*alpha_1^t coefficient (true c_j) = -0.000863512551994
  -q g_1 f_1 (h0_true - h0_implied)/alpha_1^2 = -0.000863512551994   diff = 7.6e-64
  => his coefficient is exactly proportional to the H(0) mishandling; with H(0) correct it is 0.

## F. gamma_1 < s_1 < alpha_1 on a parameter grid (and D at gamma/alpha points)
  grids tested: 125, violations of gamma_1 < s_1 < alpha_1: 0
  D at gamma_r points minus a(-1)^r: max|.| = 9.33e-61  (so s_k = gamma_r crossing impossible for beta>0)
  D at alpha_l points minus U_(L-1): max|.| = 3.42e-60  (alpha_l never a root of D)

## G. Compact amplitude form and strict positivity of B_rho_1
  grid points: 150 (N up to 40, all rho)
  compact form vs residue form: max|diff| = 6.22e-55
  min B_rho_1 over grid = 2.67421e-5  (strictly positive: dominant mode never drops out)
  T_L(y_1) in (-1,0) violations: 0

