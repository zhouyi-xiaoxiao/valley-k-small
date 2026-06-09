Corrected calculation manuscript
================================

Main file:
  Calculations_corrected_sendable.tex

Precompiled PDF:
  Calculations_corrected_sendable.pdf

Compile command:
  latexmk -pdf -interaction=nonstopmode -halt-on-error Calculations_corrected_sendable.tex

Included local dependencies:
  customcommands.sty
  customcolours.sty
  globalplotconfig.sty
  phifunction.pdf
  Calculations_corrected_sendableNotes.bib

The displayed correction is in the shortcut section. In particular, the
rank-one sign is propagated through the corrected Eq. (32), Eq. (33), the
antipodal shortcut expression, the final closed form for the first-passage
generating function, and the explicit long-time dependence governed by the
dominant root of the corrected denominator.

The appendix now records the full direct time-convolution route, including the
Eq. (41)-style long expansion, and then shows how that route recombines to the
same compact closed form. In particular, Appendix A.4 writes Eq. (58) both in
compact kernel notation and in a fully expanded partial-fraction form, including
the diagonal limits that visibly produce t alpha-type intermediate terms. After
the full expression is collected, the apparent alpha poles are removable and the
final poles are the roots of the corrected denominator. Appendix A.5 explicitly
z-transforms the expanded groups back to the generating-function route, making
the recombination step visible. Appendix B writes the apparent alpha denominator
explicitly as a removable T_L factor. Appendix C includes the numerical-validation
protocol, the summary errors, and the sampled beta bounds for the N=100, q=2/3,
n0=1,...,6 finite-time double-peak check. The local audit folder contains the
script and CSV/JSON outputs used for those checks.

2026-06-09 secular-term update. The main text (after the tail residue
expression) now states the two structural reasons why no t alpha_l^t factor
can survive: the zero of H~ at every z=1/alpha_l (the same W~_u sits in the
denominator of H~), and the symmetric/diagonalizable transient matrix whose
spectrum is {gamma_r} U {s_j} with alpha_l excluded for beta>0. Appendix A.4
ends with the explicit time-domain collection: the total coefficient of
(t-1) alpha_l^(t-2) is q f_l g_l [sum_j c_j/(s_j-alpha_l) - beta(1-q)/q],
which vanishes identically by the sum rule sum_j c_j/(s_j-alpha_l)=beta(1-q)/q
(three-line partial-fraction proof), and the spurious t alpha^t coefficient
q f_l g_l c_inf with c_inf = T_L(1-1/q)/D(1-1/q) is identified as the
time-zero boundary mismatch of the H-pole expansion (the (s^t-x^t)/(s(s-x))
kernels). Appendix C.1.1 records the corresponding 50-digit checks
(scripts/secular_term_cancellation_check.py in the local audit folder).
