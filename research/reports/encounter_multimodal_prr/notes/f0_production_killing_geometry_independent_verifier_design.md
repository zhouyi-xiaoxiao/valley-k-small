# Separate-source verifier for control-free production killing geometry

Date: 2026-07-15

Status: **LIVING DESIGN / IMPLEMENTATION IN PROGRESS / UNACCEPTED / UNAUDITED / SAME BACKEND / HOLD OPERATOR / HOLD F0**

Scope: independent-source containment verification of the compact control-free
contact and support-factor bundle. This note does not define or authorize a
concrete killing field, a full operator, a production allocation, propagation,
topology, a positive budget, F1/F2/F3, continuum evidence, or PRR release.

## 1. Decision and trust boundary

The verifier is a containment checker, not a second producer. It reconstructs
the partitions and mathematical oracles independently, then treats the
candidate bundle as an untrusted file tree.

The verifier must never import:

~~~text
rate_defined_tensor_f0_production_killing_geometry
rate_defined_tensor_f0
rate_defined_tensor_f0_production_initial_stream
~~~

It must not call a producer schema helper, producer analytic primitive, F0 core
partition builder, or initial-stream parser through a direct or transitive
alias.

The allowed numerical backend remains the pinned gmpy2/MPFR stack:

~~~text
gmpy2 = 2.2.1
MPFR = 4.2.1
GMP = 6.3.0
MPC = 1.3.1
~~~

Using a separately coded source at higher precision with this same backend and
the same composite-Simpson remainder lemma supports:

~~~text
separate_source_implementation = true
independent_backend = false
shared_simpson_remainder_lemma = true
~~~

It does not support backend independence.

The intended source target is:

~~~text
code/rate_defined_tensor_f0_production_killing_geometry_independent.py
~~~

No accepted verifier is claimed to exist; the current source remains an
in-progress implementation until the child and outer schemas, tests, two-run
receipt and independent source audit all pass on exact hashes.

## 2. Frozen inputs and a priori constants

The verifier accepts only the exact frozen authority chain:

~~~text
artifacts/data/physical_killing_geometry_source_v1.json
SHA-256 5543f76031d731cb5bcf3e4cdf3bdabaffacb2053400e3015d6ab57906a27669

artifacts/data/physical_configuration_family_control_free_v1.json
SHA-256 063913c7fbc2b706ba85a0e3f06005bad23a2292749817294cbf41f5cdce4084

artifacts/data/physical_production_initial_stream_v1/bundle.json
SHA-256 5d81d1c02ec2484f0b3d5fab3a825cf6f6331f7d3e4cc8dae224266201dfbd9e
~~~

The verifier reads the accepted partition bundle as data. It does not import
the code that produced it.

The source must freeze:

~~~text
CONFIGURATION_COUNT = 12
COORDINATES = midpoint, relative_parallel, relative_perpendicular

MPFR_PRIMARY_BITS = 384
MPFR_SENTINEL_CROSSCHECK_BITS = 512

CONTACT_CANDIDATE_INTERVAL_MAX_WIDTH = 2^-40
SUPPORT_CANDIDATE_CELL_MASS_MAX_WIDTH = 2^-40
CONTACT_ORACLE_MAX_WIDTH = 2^-180
ORACLE_TO_CANDIDATE_WIDTH_RATIO_MAX = 1/8

MAX_TREE_FILES = 256
MAX_TREE_DIRECTORIES = 64
MAX_TREE_RELATIVE_DEPTH = 3
MAX_TREE_BYTES = 67_108_864
MAX_JSON_FILE_BYTES = 2_097_152
MAX_RAW_CONTACT_FILE_BYTES = 553_840
MAX_RAW_SUPPORT_FILE_BYTES = 3_312
MAX_SIMPSON_PANELS = 4_194_304
MAX_SIMPSON_STACK_NODES = 65
MAX_SIMPSON_DYADIC_DEPTH = 64
MAX_DYADIC_COORDINATE_COMPONENT_BITS = 256
MAX_MPFR_TO_MPQ_DENOMINATOR_BITS = 4_096
MAX_SIMPSON_EXACT_COMPONENT_BITS = 8_192
MAX_BUMP_BREAKPOINTS = 20_000
BUMP_FLAT_TAIL_S_THRESHOLD = 2_048
PRIMARY_ROOT_TARGET_WIDTH = 2^-64
CHILD_SEMANTIC_DEADLINE_SECONDS = 1_140
CHILD_PROCESS_DEADLINE_SECONDS = 1_200
OUTER_NONCHILD_RESERVE_SECONDS = 300
OUTER_DEADLINE_SECONDS = 2_700
MAX_RECEIPT_BYTES = 2_097_152
MAX_CHILD_ACK_BYTES = 4_096
MAX_CHILD_OBSERVATION_BYTES = 65_536
MAX_CHILD_STDERR_BYTES = 4_096
MAX_OUTER_RECEIPT_BYTES = 262_144
PROCESS_GROUP_TERM_GRACE_SECONDS = 3
PROCESS_GROUP_KILL_WAIT_SECONDS = 2
PIPE_DRAIN_GRACE_SECONDS = 2
~~~

The two `2^-40` bounds are a priori anti-vacuity thresholds, not tolerances
fitted to producer output.  Contact fractions are dimensionless, so the bound
applies directly to their interval width.  Support payloads are densities, so
their dimensionally consistent bound applies to
`cell_volume_m * (p_hi-p_lo)`, the cell-mass interval width; applying the
contact-fraction bound directly to a density would be a units error.  Over a
relative domain of width `4.8`, the contact bound limits weighted area
inflation to below `4.8 x 2^-40`. Oracle containment itself has zero tolerance.

The exact expected raw workload is:

~~~text
contact records across 12 rows = 233_139
contact raw bytes               = 3_730_224
support records, four profiles  = 6_852
support raw bytes               = 109_632
raw interval leaves             = 60
~~~

Any count drift fails before numerical verification.

## 3. Verifier-owned function decomposition

The implementation contract is decomposed as follows:

~~~text
# Strict input and exact scalars
read_regular_stable()
strict_load_ascii_json()
parse_binary64_hex_as_fraction()
parse_reduced_fraction()
canonical_json_bytes()
digest_domain()

# Authority and configuration
load_frozen_geometry_authority()
load_control_free_configuration()
validate_configuration_order()
reconstruct_axis_partition()
reconstruct_all_partitions()
validate_accepted_partition_files()

# Candidate tree
inventory_candidate_tree()
validate_relative_manifest_path()
parse_candidate_bundle()
parse_row_manifest()
stream_be64_intervals()

# Directed MPFR interval layer
mp_interval_from_fraction()
mp_add()
mp_sub()
mp_mul()
mp_div()
mp_sqrt()
mp_asin()
mp_exp()
mp_pi()
mp_interval_to_exact_mpq_pair()

# Contact oracle
minimum_image_signed_segments()
split_rectangle_at_coordinate_axes()
disk_antiderivative_enclosure()
disk_quadrant_prefix_enclosure()
disk_rectangle_area_enclosure()
contact_fraction_oracle()
verify_contact_row()
verify_pi_r_squared_identity()

# Compact-bump oracle
bump_value_enclosure()
bump_fourth_derivative_bound()
simpson_panel_enclosure()
build_paired_shared_bump_integral_tables()
support_average_oracle()
verify_support_profile()
verify_unit_normalization()

# Comparison and receipt
require_exact_containment()
require_nonvacuous_width()
build_semantic_receipt()
run_clean_child_once()
run_serialized_two_repeat()
build_outer_repeat_receipt()
~~~

Every function and schema object is verifier-owned. No producer-defined
dataclass crosses the boundary.

## 4. Strict wire, scalar, and input rules

Every JSON input is:

- a regular, nonsymlinked, size-capped file;
- strict UTF-8 whose semantic strings and paths are ASCII;
- parsed with duplicate-key rejection;
- exact-type checked recursively;
- rejected if it contains a JSON float;
- re-encoded canonically and required to agree byte for byte; and
- hashed over the complete source bytes and complete canonical semantic body.

Binary64 hex values are parsed directly into exact rational values. The
authority is not first converted through a Python float. The parser must:

1. validate one canonical sign/mantissa/exponent grammar;
2. reconstruct the exact dyadic rational;
3. reject NaN, infinity, noncanonical zero, alternate spellings, overflow and
   underflow aliases; and
4. independently round the rational to binary64 and require the canonical
   `float.hex()` spelling to agree.

Exact rational strings require:

~~~text
denominator > 0
gcd(abs(numerator), denominator) = 1
one canonical zero = 0/1
~~~

Candidate interval leaves use exact big-endian `>dd` records. The verifier
extracts each endpoint as exact binary64 bits and exact dyadic rational before
comparison.

## 5. Exact partition reconstruction from the control-free configuration

The configuration order, labels, axis roles, alignments, sizes, shapes,
expected state counts and binary64 bounds are validated before reconstruction.
Unknown alignments or optional replacements fail closed.

### 5.1 Cell-centred reflecting

For exact lower `L`, upper `U` and size `n`:

~~~text
h = (U-L)/n
position_i = L + (i+1/2)h
cell_i = [L+ih, L+(i+1)h]
volume_i = h
~~~

The cells must be ordered, nonoverlapping, cover `[L,U]` exactly and have
positive volume.

### 5.2 Vertex-centred reflecting dual

~~~text
h = (U-L)/(n-1)
position_i = L+ih

boundaries =
    L,
    (position_0+position_1)/2,
    ...,
    (position_(n-2)+position_(n-1))/2,
    U
~~~

Endpoint dual-cell volumes are `h/2`; all interior volumes are `h`. The
verifier rejects substitution of a cell-centred grid or full endpoint volume.

### 5.3 Periodic cell-centred

The transverse period is the exact rational one:

~~~text
h = 1/n
shift = 0       for cell_centred_periodic_base
shift = h/2     for cell_centred_periodic_half_shift

position_i = mod((i+1/2)h+shift, 1)
cell_i = [mod(ih+shift,1), mod((i+1)h+shift,1)]
~~~

A cell crossing the identified endpoint is represented by exactly two ordered
segments. The configuration's `periodic_shift_exact` must equal the derived
shift.

### 5.4 Cross-checks

For every row the verifier:

- requires `shape` to equal the three reconstructed axis sizes;
- recomputes the shape product and requires `expected_states`;
- compares every accepted partition-file boundary, segment, position and
  volume as an exact rational;
- binds a verifier-owned canonical partition-semantic digest;
- requires candidate factor manifests to reference the accepted partition
  bytes and axis-relation hashes; and
- requires the candidate row relation to bind the independent reconstruction
  digest.

No accepted row summary substitutes for these checks.

## 6. Directed MPFR interval layer

The verifier implements one small immutable interval type:

~~~text
MPInterval(lower, upper, precision_bits)
~~~

It rejects nonfinite values, wrong precision, and `lower > upper`.

Exact rational inputs are converted outward. Arithmetic uses full interval
rules rather than one global rounding direction:

~~~text
[a,b] + [c,d] = [add_down(a,c), add_up(b,d)]
[a,b] - [c,d] = [sub_down(a,d), sub_up(b,c)]

[a,b] * [c,d] =
    [min_down(ac,ad,bc,bd), max_up(ac,ad,bc,bd)]
~~~

Division is allowed only after proving the denominator interval excludes zero.
Square root, exponential and arcsine use monotonic directed endpoints on their
validated domains.

Every final MPFR endpoint is converted to the exact dyadic `mpq` represented
by that MPFR value. Containment comparisons are exact rational comparisons,
never binary64 comparisons.

## 7. Higher-precision contact oracle

### 7.1 Periodic minimum-image rectangles

The verifier independently proves `2r < 1` using exact rationals. Each periodic
transverse cell segment is converted to signed minimum-image coordinates in
`[-1/2,1/2]`. Segments are split at the identified endpoint, cut locus and zero
where necessary.

Every resulting signed rectangle is classified with exact rational arithmetic:

~~~text
zero:
    nearest_corner_distance_squared >= r^2

full:
    farthest_corner_distance_squared <= r^2

partial:
    otherwise
~~~

Measure-zero tangency is zero area. A complete cell classified zero or full
must be saved exactly as `[0,0]` or `[1,1]`.

### 7.2 Independent disk-rectangle primitive

For `0 <= a,b <= r` define:

~~~text
A(t) = 1/2 [t sqrt(r^2-t^2) + r^2 asin(t/r)]
x_b = sqrt(r^2-b^2)

Q(a,b) =
    a b                         if a^2+b^2 <= r^2
    b x_b + A(a)-A(x_b)         otherwise
~~~

Inputs are clipped at `r`. A quadrant rectangle is obtained by
inclusion-exclusion of four `Q` values. Arbitrary signed rectangles are split
across coordinate axes and summed.

Every `sqrt` and `asin` expression is evaluated through the interval layer.
Subtraction uses upper subtrahends for lower bounds and lower subtrahends for
upper bounds. The implementation must not evaluate the displayed formula once
under `RoundDown` and once under `RoundUp` while ignoring dependency direction.

### 7.3 Contact fraction and global identity

For a relative cell with exact volume `V_ab`:

~~~text
C_ab = enclosed contact area / V_ab
~~~

The independent oracle is computed at 384 bits. The full-disk and sentinel
partial cells are recomputed at 512 bits; each 512-bit interval must be
contained in the corresponding 384-bit interval.

The verifier obtains a directed interval for pi from MPFR and requires in every
row:

~~~text
sum_ab V_ab * C_ab contains pi*r^2
~~~

This identity is valid because every frozen parallel box contains `[-r,r]` and
the cut-locus condition prevents disk overlap.

## 8. Independently coded normalized compact-bump oracle

The authority defines:

~~~text
b(u) = exp(-1/(1-u^2))   for abs(u)<1
b(u) = 0                 for abs(u)>=1

I_b = integral_[-1,1] b(u) du
~~~

For midpoint cell `M_m`, support centre `c_j` and support half-width `h_s`:

~~~text
u = (M-c_j)/h_s

Phi_jm =
    integral_[u_lo,u_hi] b(u) du
    / (cell_volume_m * I_b)
~~~

The change of variables cancels the explicit `h_s` in the normalized density.
Cells disjoint from `[c_j-h_s,c_j+h_s]` are exact zero.

### 8.1 Shared breakpoint table

Gather every exact transformed midpoint-cell endpoint for all 12 rows and four
profiles. Clip to `[-1,1]`, add `-1,0,1`, sort, deduplicate, and require no more
than `MAX_BUMP_BREAKPOINTS`.

The verifier integrates the bump once over this shared ordered table. It does
not rerun a separate unconstrained quadrature for every cell.

### 8.2 Rigorous Simpson remainder

For one Simpson panel `[a,b]`:

~~~text
S = (b-a)/6 [f(a)+4f((a+b)/2)+f(b)]
error <= (b-a)^5 M4 / 2880
~~~

Set `s=1/(1-u^2)`. A separately derived local fourth-derivative bound is:

~~~text
abs(b''''(u)) <= exp(-s) [
    24 s^3 + 300 s^4 + 672 s^5
  + 624 s^6 + 192 s^7 + 16 s^8
]
~~~

For each monomial, `s^k exp(-s)` is maximized at `s=k`.  For each exact shared
breakpoint root segment, evaluate every positive term at its exact clamped
maximizer and round upward.  The resulting root-local `M4` bounds every
dyadic descendant because each descendant is a subset of that root.  The
verifier computes one such bound at 384 bits and one at 512 bits and requires
the exact inequality `M4_512 <= M4_384`.

The endpoint is protected by a separate analytic flat-tail policy.  With
`T=2048` and `s=1/(1-u^2)`, `e>2` gives
`exp(-s) < 2^-s <= 2^-T` whenever `s>=T`.  Hence the closed interval
`[0,2^-T]` is a valid bump-value enclosure.  Since
`d(s^k exp(-s))/ds = s^(k-1) exp(-s)(k-s)`, every term for `3<=k<=8` is
decreasing on `[T,infinity)`, so a root wholly inside this tail uses the exact
bound

~~~text
sum_(k=3)^8 c_k T^k 2^-T,
(c_3,...,c_8) = (24,300,672,624,192,16).
~~~

At `abs(u)=1` the extended bump and all derivatives remain exact zero.  The
tail policy is domain-separated and receipt-bound; it is a hard rational-size
guard, not a fitted truncation tolerance.

The 384-bit refinement uses a deterministic segment-order, left-first depth-
first traversal.  A live node contains its dyadic identity and the immutable
three-point samples at both precisions.  Splitting computes only the quarter
and three-quarter samples; the children reuse the parent endpoints and
midpoint.  The exact root-local remainder for a segment and depth is cached,
as are the exact allowance and directed `(b-a)/6` scale.  The fixed arithmetic
order is

~~~text
f(a) + (4*f(midpoint) + f(b)), then multiply by (b-a)/6.
~~~

Before evaluating that weighted estimate, the verifier compares the exact
remainder `R` with the node allowance.  Every nonnegative Simpson enclosure
has width at least `R`; therefore `R > allowance` proves that the node must be
split and permits the estimate to be skipped.  Equality does not prove a
split and follows the ordinary exact panel-width comparison.

Bisect until every accepted 384-bit leaf meets
`PRIMARY_ROOT_TARGET_WIDTH/2^depth`.  This predicate is node-local and has no
global remaining-width or early-stop state.  Consequently every complete
traversal produces the same terminal leaf set; traversal order affects only
resource timing.  The accepted leaves are prefix-free, so the sum of their
allocations is at most the root target width, and the completed exact
enclosure is checked against that bound again.  Exact rational accumulation
is associative and does not change this leaf-set argument.

The 512-bit sentinel follows exactly the accepted 384-bit leaf tree; it is not
a second adaptive run and makes no `2^-68` claim.  Both precisions evaluate
the same expression DAG.  The verifier requires every 512-bit sample interval
to lie inside its 384-bit counterpart, every 512-bit root `M4` to be no larger
than the 384-bit root bound, and every accepted 512-bit panel to lie inside
the corresponding 384-bit panel.  Exact interval addition then proves table
and normalizer nesting.  Positive interval division proves the same nesting
for every support-cell oracle, not merely a selected example.

Reject a requested child before retaining any tree object beyond
`MAX_SIMPSON_DYADIC_DEPTH`, retain at most `MAX_SIMPSON_STACK_NODES`, and
enforce the panel and time caps before the next retained node.  Coordinate
results and every exact remainder, panel endpoint and accumulator numerator
and denominator are checked immediately after each bounded operation against
their respective caps.  The flat-tail branch and the MPFR exponent/precision
precheck occur before an unbounded near-endpoint or MPFR-to-`mpq` conversion.
Exceeding any cap is HOLD and never relaxes the producer-width gate.

In particular, the operands and the resulting exact transformed breakpoint or
dyadic child are checked against
`MAX_DYADIC_COORDINATE_COMPONENT_BITS`.  A nonzero MPFR endpoint is inspected
before conversion; its precision and binary exponent must imply an exact
dyadic denominator no larger than
`MAX_MPFR_TO_MPQ_DENOMINATOR_BITS`.  The common checked conversion wrapper is
the only support-Simpson path allowed to call `mpq(mpfr)`.  The resulting
numerator/denominator and every subsequent exact accumulator are then checked
against `MAX_SIMPSON_EXACT_COMPONENT_BITS`.  Only the MPFR conversion claims a
pre-allocation denominator/numerator guard.  Ordinary Fraction/MPQ arithmetic
is checked immediately after construction and is bounded for this frozen
workload by the operand, coordinate and depth caps; it is not advertised as a
general allocation-free preflight theorem.

The semantic receipt binds separate domain-separated refinement-policy and
tail-policy digests.  It records the primary node and accepted-leaf counts,
maximum dyadic depth and live stack, per-precision sample counts, skipped-
estimate count, weighted-estimate counts, tail-branch counts, maximum exact-
component bit lengths, and all sample/root/panel/table/support nesting counts.
These are algorithm observations, not a production resource promotion.

### 8.3 Normalizer lower bound and global identity

The verifier proves independently:

~~~text
I_b
  >= integral_[-1/2,1/2] exp(-4/3) du
  > 1/4
~~~

The computed normalizer interval must lie strictly above `1/4`.

For every row and every support profile:

~~~text
sum_m cell_volume_m * Phi_jm contains 1
~~~

The normalizer and every support-cell oracle are recomputed at 512 bits on the
same accepted 384-bit leaf tree.  Their 512-bit intervals must be contained in
the 384-bit intervals.  This is a same-leaf precision-nesting check, not a
second adaptive tolerance and not a second backend.

## 9. Containment and anti-vacuity rules

Let the candidate producer interval be `[p_lo,p_hi]` and the verifier oracle
be `[v_lo,v_hi]`. Acceptance requires exact rational inequalities:

~~~text
p_lo <= v_lo
v_hi <= p_hi
~~~

There is no additive or relative containment tolerance.

Every nonexact contact candidate interval requires:

~~~text
p_hi - p_lo <= CONTACT_CANDIDATE_INTERVAL_MAX_WIDTH
v_hi - v_lo <= (p_hi-p_lo)/8
~~~

Every nonexact support-density candidate in midpoint cell `m` instead
requires:

~~~text
cell_volume_m * (p_hi-p_lo) <= SUPPORT_CANDIDATE_CELL_MASS_MAX_WIDTH
cell_volume_m * (v_hi-v_lo) <= cell_volume_m * (p_hi-p_lo)/8
~~~

The analytic contact oracle additionally requires:

~~~text
v_hi - v_lo <= 2^-180
~~~

The Simpson table is refined until the one-eighth rule holds. A narrow
candidate interval therefore demands a narrower oracle; it does not receive a
larger tolerance.

Exact zero/full contact cells and exact outside-support cells require exact
binary64 endpoint pairs. Negative zero is rejected.

For each row, exact rational weighted sums are reconstructed from the
candidate binary64 endpoints.  The contact aggregate width is bounded by the
sum of relative-cell volumes times the contact cap.  Each support aggregate
must satisfy the producer-frozen `1/10^10` mass-width cap independently of the
per-cell anti-vacuity check.  The contact sum must contain `pi r^2` and each
support sum must contain one.

## 10. File, manifest, and tree closure

Before numerical work the verifier:

1. validates the frozen authority, configuration and accepted partition
   hashes;
2. rejects an absolute path, `.`, `..`, NUL, empty component, non-ASCII
   component or noncanonical separator;
3. rejects symlinks, nonregular files, hard-link aliases and duplicate
   `(device,inode)` identities;
4. enforces per-file, file-count, directory-count, relative-depth and
   total-tree caps before reading or enqueueing the next node;
5. records `lstat/fstat` identity, size and timestamps before and after each
   read and rejects change;
6. requires exact inventory closure with no missing, duplicate, reordered,
   unreferenced or extra file;
7. requires exactly 12 rows in frozen configuration order;
8. requires one contact and four support raw leaves per row;
9. verifies exact `>dd` byte lengths, record counts and SHA-256 values;
10. rejects NaN, infinity, negative zero, reversed endpoints and noncanonical
    zeros;
11. requires contact endpoints in `[0,1]` and support endpoints finite and
    nonnegative;
12. recomputes every row and family relation digest; and
13. requires every configuration/partition reference to match both accepted
    bytes and independent semantic reconstruction.

The candidate schema may still be moving while this note is written. Source
implementation begins only after that schema freezes. The independent source
then copies literal schema names, key sets and domains into verifier-owned
constants; it does not import the producer.

## 11. Mandatory mutation matrix

Every mutation returns one exact HOLD status, no partial success receipt, no
unbounded error detail, and no live child after ordinary cleanup.

### 11.1 Authority and partitions

- authority, configuration or accepted partition hash change;
- row omission, duplication or reordering;
- shape/product/expected-state mismatch;
- reflecting/cell-centred/vertex-dual substitution;
- full endpoint volume substituted for half volume;
- base/half-periodic shift substitution;
- wrong wrap segmentation or duplicate periodic endpoint;
- midpoint/parallel/transverse coordinate swap; and
- partition byte reference that agrees with producer but not independent
  reconstruction.

### 11.2 Contact oracle

- radius or period bit change;
- removed or weakened `2r<1` check;
- Euclidean transverse distance substituted for minimum-image distance;
- disk quadrant, antiderivative, inclusion-exclusion or sign split mutation;
- `pi r^2` replaced by a rounded binary64 constant;
- zero/full/partial classification mutation;
- exact zero/full cell widened;
- one-ulp endpoint narrowing that excludes the oracle; and
- vacuously wide producer interval that still contains the oracle.

### 11.3 Support oracle

- support centre, half-width or profile-order mutation;
- missing normalization or cell-volume division;
- reuse of the initial-source half-width;
- cell outside compact support made nonzero;
- Simpson node changed from three nodes/two subintervals, wrong midpoint, or
  changed `1-4-1` weights/association;
- factor `1/2880` changed;
- one derivative coefficient changed or derivative bound lowered;
- child-local or global `M4` substituted for the frozen root-local contract;
- 512 evaluation moved to a different leaf tree or mislabeled `2^-68`;
- flat-tail threshold, value cap, derivative cap or policy digest changed;
- `R > allowance` prefilter weakened to `>=` or applied in the opposite direction;
- normalizer lower-bound removal;
- unit-integral containment failure;
- stack, depth, panel, exact-component cap bypass or tolerance relaxation; and
- 384/512-bit cross-check reversal.

### 11.4 Wire and tree

- duplicate JSON key or JSON float;
- endian swap, record truncation or appended byte;
- manifest count, length, hash or relation change;
- symlink, hard link, path traversal, alias or extra file;
- changed-during-read replacement;
- pre-existing output;
- producer/F0/initial-stream direct or transitive import; and
- forbidden runtime module appearing after import-boundary closure.

### 11.5 Repeat protocol

- same PID reused for both claimed runs;
- run-one/run-two deterministic semantic difference;
- nonzero exit, stderr, timeout or oversized output;
- observation fields inserted into the deterministic semantic body;
- stale semantic receipt replayed against changed input; and
- unconfirmed cleanup represented as PASS.

## 12. Clean-process serialized two-repeat protocol

There are two disjoint acceptance layers.  A child may certify one
deterministic semantic verification, but it may not claim clean replay.  Only
an outer observer that has completed two serialized child runs may issue the
downstream-consumable acceptance receipt.

The current candidate wire contract is recorded separately in
`code/rate_defined_tensor_f0_production_killing_geometry_independent_operation_model_v2.json`.
Its canonical byte length is `12,956` and its SHA-256 is
`53f709139c380e9512740a6fdabcd7570c1822650817915454ddbd7d7395feb0`.
Version 2 now freezes the exact
success/HOLD emission schemas, the domain-separated input-snapshot encoding
and the EOF/reap cleanup predicates for implementation.  This is a frozen
implementation specification, not an accepted outer result: the exact runner,
mutation tests and two serialized clean runs still have to satisfy it.
Neither executable accepts a timeout, cap, runtime, source, environment or
repeat-count override.  The outer executable has only this public wire:

~~~text
<resolved-python> -I -B
  <absolute-run_rate_defined_tensor_f0_production_killing_geometry_independent_replay.py>
  --report-root <absolute-report-root>
  --bundle <absolute-candidate-root>
  --outer-receipt <previously-absent-path>
~~~

The outer observer launches two distinct serialized processes with this
frozen wire shape:

~~~text
<absolute-verified-venv-python-launcher> -I -B
  <absolute-staged-independent-verifier-source>
  --report-root <private-staged-report-root>
  --bundle <private-staged-candidate-root>
  --semantic-receipt <previously-absent-path>
  --observation <previously-absent-path>
  --launch-nonce <outer-generated-256-bit-hex>
  --run-index <0-or-1>
~~~

Each run uses:

- an exact five-key environment, with no inherited entries:

  ~~~text
  HOME=<private-stage>/home
  TMPDIR=<private-stage>/tmp
  LANG=C
  LC_ALL=C
  TZ=UTC
  ~~~

  The two path values are freshly created `0700` directories and the other
  three values are literal ASCII strings.  This is the exact mapping supplied
  by the parent to `Popen`; Darwin may add `__CF_USER_TEXT_ENCODING` inside the
  child, which is an operating-system insertion rather than an inherited
  parent entry;
- a private `0700` working directory outside synchronized storage;
- `stdin=DEVNULL`, `close_fds=true`, `start_new_session=true` and no shell;
- no imported or requested network API, while honestly recording
  `os_network_isolation=false` unless an independently tested operating-system
  sandbox is later added;
- absent output paths;
- exact runtime, dependency and verifier-source hashes;
- a distinct PID;
- nonblocking selector-based bounded stdout/stderr capture;
- an internal semantic deadline of
  `CHILD_SEMANTIC_DEADLINE_SECONDS=1140`, a per-child process deadline of
  `CHILD_PROCESS_DEADLINE_SECONDS=1200`, one outer-state-machine monotonic
  deadline of `OUTER_DEADLINE_SECONDS=2700`, and the frozen output caps; and
- complete descriptor/temp cleanup.

Each child emits:

1. `semantic.json`, a deterministic canonical semantic receipt;
2. `child_observation.json`, a separate observation body containing the
   launch nonce, run index, PID/PPID/PGID, elapsed time, physical-resource
   observations and file hashes; and
3. one canonical ASCII JSON stdout acknowledgement no larger than
   `MAX_CHILD_ACK_BYTES`, binding the two file hashes, child-only status,
   schema, nonce and run index.

Both output files must be newly created regular nonsymlinked single-link data,
closed before acknowledgement, stably reread by the outer process and bounded
by `MAX_RECEIPT_BYTES` and `MAX_CHILD_OBSERVATION_BYTES`, respectively.
Stdout and stderr are capped separately by `MAX_CHILD_ACK_BYTES` and
`MAX_CHILD_STDERR_BYTES`; stderr must be empty.  The child-reported PID must
equal `Popen.pid`, the process group must initially equal that PID, and the
nonce/run index must match the launch request.

The exact child emission matrix is fail closed.  Success publishes the full
semantic success schema, then the observation schema, then a bound stdout
acknowledgement and exits zero.  A semantic HOLD after the complete CLI and
both absent output paths have been validated publishes a two-key semantic HOLD
file, an observation with the same HOLD status, and the same bound
acknowledgement shape before exiting two.  If the CLI/output paths cannot be
safely resolved or the complete two-file wire cannot be published, no partial
file is consumable: stdout contains only the two-key unbound-HOLD schema with
`HOLD_KILLING_GEOMETRY_VERIFY_API`, stderr remains empty and the child exits
two.  Each file is created with `O_EXCL|O_NOFOLLOW`, closed and stably reread
before the next file or acknowledgement is emitted.

The two deterministic semantic receipt bodies must agree byte for byte. The
observation bodies need not agree.  Comparing parsed dictionaries or only
claimed digests is insufficient.

The deterministic semantic body may contain source/runtime/dependency pins,
the separately reconstructed mathematical evidence, and all nonpromotion
flags.  It must not contain PID, run index, nonce, time, RSS/CPU, inode/device,
timestamps, private paths, stdout/stderr, exit status or cleanup observations.
Its verifier-source hash denotes the stably reread staged file; a child receipt
alone does not attest that those bytes were the already executing Python code
object.  Only the outer layer's private staged source, exact launch command and
matching pre-copy, pre-run and post-run snapshots may consume the child result.

The input snapshot is a finite domain-separated tuple, not a scan of the
shared worktree.  It binds separately:

~~~text
complete candidate killing-geometry tree
complete accepted partition tree
authority and control-free configuration bytes
producer, producer-test, F0-core and initial-stream source hash pins
design bytes, independent-verifier source and operation-model bytes
verified venv launcher chain, resolved runtime-executable target and gmpy2
extension bytes/version strings
~~~

These are thirteen ordered components.  A file component binds its role,
complete byte length and SHA-256.  Each tree component binds a sorted ASCII
list of all relative files with complete byte lengths and SHA-256 values plus
all directories including `.` so that empty directories are not invisible.
The canonical snapshot body has exactly `components`, `runtime_versions` and
`schema`; its digest is
`SHA256(b"encounter-killing-geometry-input-snapshot-v1\0" + snapshot_bytes)`.
Absolute paths, stage names, inode, device, mode and timestamps are excluded.
The child executes the absolute outer `sys.executable` venv launcher because
executing only its physically resolved Homebrew target loses the venv and its
pinned gmpy2 installation.  The launcher symlink chain is checked for
pre-launch/post-exit stability, while the resolved regular target bytes are
the `runtime_executable` snapshot component.

Candidate and accepted-partition tree caps apply separately.  Before each run,
the outer observer copies the bounded input closure by bytes into a fresh
private stage (never with hard links), recomputes the staged snapshot, and
makes staged inputs read-only.  For each run it retains the complete canonical
bytes at `origin_pre_copy`, `stage_post_copy`, `stage_pre_launch` and
`stage_post_exit`.  All eight bodies across runs zero and one must be byte for
byte equal, and all eight independently recomputed domain-separated hashes
must agree.  Parsed-object equality or digest equality alone is not a
substitute.  The post-exit snapshot is taken after the direct child is reaped,
the group is absent and both pipe EOFs are observed, but before stage removal.

The outer receipt binds:

~~~text
verifier source and operation-model hashes
runtime and gmpy2/GMP/MPFR/MPC versions
complete input-tree snapshot hash
run-one and run-two semantic body hashes
byte-identical semantic-body result
distinct child PIDs
exit codes
stdout and stderr hashes
deadline observations
cleanup results
~~~

The outer state machine is strictly serialized:

~~~text
precheck and canonical snapshot
stage, launch, capture, validate and post-snapshot child 0
reap child 0, confirm group and both EOFs, close selector, remove stage 0
repeat canonical snapshot
stage, launch, capture, validate and post-snapshot child 1
reap child 1, confirm group and both EOFs, close selector, remove stage 1
compare complete semantic receipt bytes
build, exclusively publish and reread the outer receipt
emit outer PASS acknowledgement last
~~~

The outer deadline covers that complete state machine, not two independent
2700-second child allowances.  The arithmetic is frozen as
`2*1200 + 300 = 2700`: at least `OUTER_NONCHILD_RESERVE_SECONDS=300` is reserved
for both staging passes, bounded capture, termination, pipe drain, snapshot
checks, publication and cleanup.  Before either launch the observer checks the
remaining global time against the current child allowance plus the reserved
work still outstanding; insufficient time is a timeout HOLD before launch.

Timeout or bounded-output overflow terminates the complete process group with
`SIGTERM`, polls for absence for at most
`PROCESS_GROUP_TERM_GRACE_SECONDS`, then sends
`SIGKILL` if required, waits `PROCESS_GROUP_KILL_WAIT_SECONDS`, and drains
closed pipes for at most `PIPE_DRAIN_GRACE_SECONDS` before an explicit
process-group absence check.  Both nonblocking pipes are drained concurrently
while the parent and group are polled.  Every path explicitly waits for and
reaps the direct child, obtains its exit code, and separately observes
`read()==b""` on stdout and stderr; closing a parent read descriptor is not an
EOF observation.  Only then are both descriptors unregistered and closed and
the empty selector closed.  Normal parent exit with a live descendant is also
cleanup failure.  Any failure returns no outer PASS receipt. Temporary files
and directories are removed before an ordinary HOLD is returned.  Unconfirmed
direct-child reap, process-group death, either pipe EOF/closure, selector
closure or stage removal maps to `HOLD_KILLING_GEOMETRY_VERIFY_CLEANUP` and
overrides an earlier ordinary HOLD.  A timeout with confirmed cleanup maps to
`HOLD_KILLING_GEOMETRY_VERIFY_TIMEOUT`.

The outer receipt is published with `O_CREAT|O_EXCL|O_NOFOLLOW`, is capped by
`MAX_OUTER_RECEIPT_BYTES`, is closed and stably reread before the final stdout
acknowledgement, and is never overwritten or replaced.  Direct source launch
does not prove that a child-reported hash describes already executing code;
the semantic body therefore keeps
`verifier_executed_source_attested=false`.  The outer layer attests only the
private staged launch path and its matching pre-run/post-run byte snapshots.
An outer HOLD never retains an outer receipt.  If this process created a
receipt but stable reread or final acknowledgement preparation fails, it may
remove only that newly created file and must confirm absence; it never removes
a path that existed before launch.  Success and HOLD acknowledgements use
different exact schemas: success binds receipt length and hash, whereas HOLD
is the two-key outer-HOLD schema.

## 13. Exact statuses

One child semantic verification uses this explicitly non-final status:

~~~text
PASS_CONTROL_FREE_KILLING_GEOMETRY_SEPARATE_SOURCE_SAME_BACKEND_CONTAINMENT_CHILD_ONLY_NOT_CLEAN_REPLAY_NOT_CONCRETE_KILLING_NOT_FULL_OPERATOR_NOT_F0_NOT_F1
~~~

The sole downstream-consumable success status is:

~~~text
PASS_TWO_REPEAT_CLEAN_PROCESS_CONTROL_FREE_KILLING_GEOMETRY_SEPARATE_SOURCE_SAME_BACKEND_CONTAINMENT_ONLY_NOT_CONCRETE_KILLING_NOT_FULL_OPERATOR_NOT_F0_NOT_F1
~~~

Child and outer receipts use different exact schemas.  Downstream code must
reject the child schema/status even when its mathematical fields pass.

The source and outer runner freeze this ordered HOLD enum:

~~~text
HOLD_KILLING_GEOMETRY_VERIFY_API
HOLD_KILLING_GEOMETRY_VERIFY_SOURCE
HOLD_KILLING_GEOMETRY_VERIFY_IMPORT_BOUNDARY
HOLD_KILLING_GEOMETRY_VERIFY_TREE
HOLD_KILLING_GEOMETRY_VERIFY_MANIFEST
HOLD_KILLING_GEOMETRY_VERIFY_PARTITION
HOLD_KILLING_GEOMETRY_VERIFY_CONTACT_ORACLE
HOLD_KILLING_GEOMETRY_VERIFY_SUPPORT_ORACLE
HOLD_KILLING_GEOMETRY_VERIFY_CONTAINMENT
HOLD_KILLING_GEOMETRY_VERIFY_WIDTH
HOLD_KILLING_GEOMETRY_VERIFY_NORMALIZATION
HOLD_KILLING_GEOMETRY_VERIFY_REPEAT
HOLD_KILLING_GEOMETRY_VERIFY_TIMEOUT
HOLD_KILLING_GEOMETRY_VERIFY_CLEANUP
~~~

Within one object, the earliest entry is primary. Across protocol time, the
first detected failure is primary except that unconfirmed process, pipe or
temporary-stage cleanup always upgrades the result to
`HOLD_KILLING_GEOMETRY_VERIFY_CLEANUP`.

## 14. Exact success flags and nonclaims

Each child deterministic semantic receipt must contain the following common
mathematical flags, but must omit repeat, PID, observation and cleanup fields:

~~~text
separate_source_implementation                     = true
independent_backend                               = false
shared_simpson_remainder_lemma                    = true
producer_module_imported                          = false
f0_core_imported                                  = false
initial_stream_imported                           = false
partitions_reconstructed_from_control_free_config = true
directed_mpfr_contact_oracle                      = true
independent_simpson_remainder_source              = true
producer_envelopes_contain_independent_oracles    = true
contact_pi_r_squared_enclosed_all_rows            = true
support_unit_integral_enclosed_all_rows_profiles  = true
candidate_width_caps_passed                       = true

killing_geometry_bound                            = true
concrete_killing_constructed                      = false
single_physical_operator_bound                    = false
full_operator_bound                               = false
installed_budget_used                             = false
prospective_control_used                          = false
positive_budget_executed                          = false
science_executed                                  = false
propagation_executed                              = false
topology_complete                                 = false
production_resource_gate                          = false
resource_promotion_eligible                       = false
largest_state_tensor_allocated                    = false
continuum_verified                                = false
f0_pass                                           = false
f1_authorized                                     = false
prr_release_authorized                            = false
~~~

Only the outer receipt adds:

~~~text
clean_process_repeat_count                        = 2
semantic_receipt_bytes_identical                  = true
distinct_child_pids                               = true
serialized_child_execution                        = true
child_process_groups_cleaned                      = true
temporary_stages_removed                          = true
os_network_isolation                              = false
pinned_source_requests_no_network_api             = true
full_binary_dependency_filesystem_closure          = false
~~~

The last three boundary fields are intentionally honest: sanitized environment
and an import boundary are not an operating-system network sandbox, and the
runtime executable plus gmpy2 extension/version pins do not snapshot the full
Python standard library, dynamic-library or kernel filesystem closure.  If a
stronger operating-system or full-binary attestation layer is later added,
that is a new operation-model hash and design review.

No caller may alter a false nonpromotion field. The receipt contains no
candidate arrays, MPFR objects, file descriptors, private paths, mutable
containers or unbounded exception strings.

## 15. Expected runtime and memory

The verifier reads about `3.84 MiB` of raw interval data and never constructs
an `N`-state killing array.  The child decodes the complete compact
contact/support payload into exact interval tuples.  After the complete
contact oracle and aggregate checks pass, it constructs a support-phase view
that retains rows, axes, support tuples, tree snapshots and receipt metadata
but drops all 233,139 contact intervals before quadrature.  This is an explicit
phase-lifetime reduction, not a row-streaming claim.

Most of the 233,139 contact cells classify exactly as zero or full. Only cells
intersecting the disk boundary require MPFR `sqrt`/`asin`. Of the 6,852
support cell/profile records, most are exact zero; the nonzero cells share the
paired root-local table and one 384-bit refinement tree.  The preimplementation
full-workload prototype observed 234,278 primary tree nodes, 117,213 accepted
leaves, complete 512-in-384 nesting, 6,852/6,852 producer containments, about
10.4 seconds wall time and 357,351,424 bytes peak RSS while still retaining the
candidate.  Those numbers are design evidence only until reproduced by the
exact source and clean-process runner.

The planning envelope per clean run is:

~~~text
expected wall time       below 5 minutes
hard protocol deadline   45 minutes
expected observed RSS    below 512 MiB
raw input payload        below 4 MiB
temporary/tree cap       64 MiB
receipt cap              2 MiB
~~~

These are engineering expectations, not accepted resource claims. RSS,
allocator behaviour, MPFR native allocations, page cache, scheduling and
cleanup latency remain observations.

The verifier sets:

~~~text
production_resource_gate = false
resource_promotion_eligible = false
~~~

regardless of observed runtime. It verifies compact killing geometry only.

## 16. Acceptance and stop conditions

The design and in-progress implementation remain unaccepted and unaudited
until all of the following exist on exact hashes:

- frozen candidate bundle schema and relation domains;
- independent source with the forbidden-import boundary;
- exact partition reconstruction tests for all four alignment contracts;
- directed contact-oracle and `pi r^2` tests;
- independent bump/Simpson/remainder tests;
- complete containment, width, normalization and tree mutation suites;
- two clean serialized process repeats;
- exact receipt/status/nonpromotion validation; and
- a new independent exact-hash source and numerical-correctness audit.

Current conclusion:

~~~text
INDEPENDENT VERIFIER DESIGN REVISED
IMPLEMENTATION IN PROGRESS / UNACCEPTED
SOURCE AUDIT ABSENT
SAME NUMERICAL BACKEND
CONCRETE KILLING ABSENT
FULL OPERATOR HOLD
RESOURCE PROMOTION ABSENT
F0 HOLD
F1/F2/F3 NOT AUTHORIZED
CONTINUUM NOT VERIFIED
PRR RELEASE HOLD
~~~
