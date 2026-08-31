# Result-blind fixed-`B` allocation-cusp discovery protocol v6

Date: 2026-07-14  
Status: **Round-85 v6 implementer repair; HOLD-INDEPENDENT-PRERUN before any mesh-65/97 evaluation**

## 1. Purpose and evidence boundary

This is the result-blind v6 Stage-A discovery chain required by the fixed-budget
allocation-cusp promotion design and the Round-44 scaffold audit.  Its only
scientific meshes are the baseline-box cubic meshes `65` and `97`.  They are
discovery meshes.  Neither is held out, and neither may be described as
continuum, parity, box, or independent-solver confirmation.

The formal result and reproducibility paths were absent when this protocol and
its manifest were frozen.  The runner was exercised only through unit tests and
small explicit-CSR dry runs.  In particular, preparation of this package did
not evaluate the allocation cusp, its folds, the remote pair, or any of the 32
phase controls on mesh 65 or 97.

Rounds 61, 74, 80, 83, and the independent Round-84 review found defects in the earlier freezes. This v6 protocol closes
the enumerated implementer repairs without inspecting or producing any
scientific mesh result and pins both reports and regression suites.  The only
possible successful status is `PASS_DISCOVERY_LOW_MESH_ONLY`.  It
authorizes the separate no-refit Stage-B freeze; it is not a manuscript claim
or a publication gate.

## 2. Immutable physical family

The manifest fixes

\[
D=0.002,\quad \gamma=0.1,\quad \bar m=0.95,\quad W=1,
\quad a=0.16,\quad B=0.01.
\]

It also fixes midpoint start `0.14`, relative start `(-0.35,0)`, initial
half-width `0.02`, patch half-width `0.04`, slab centres
`(0.35,0.60,0.75,0.90)`, midpoint faces `[-0.25,1.85]`, and relative-parallel
faces `[-1.8,1.8]`.  Stage A may move only the four unit-sum nonnegative
allocation weights.  It may not tune transport, supports, box, budget, initial
law, or contact geometry.

## 3. Frozen allocation chart

The chart is determined entirely from the repository's pre-existing `B=0`
full-simplex response.  With

\[
w_c^{(0)}=(0.28,0.23115240260064182,0.20722533378296604,
0.28162226361639210),
\]

the coordinates are

\[
w(\theta)=w_c^{(0)}+P\theta,
\]

\[
P=\begin{pmatrix}
-0.0333951724537727& 0.0474675452740631\\
-0.588571155923409&-0.569871639404847\\
 0.790069638665939&-0.256745888525331\\
-0.168103310288757& 0.779149982656115
\end{pmatrix}.
\]

The columns are the two right-singular response directions ordered by
decreasing nonzero singular value; each sign makes its largest-magnitude
component positive.  The Euclidean allocation metric, all printed digits,
column order, and sign rule are immutable.

## 4. Cusp equations and exact sensitivities

For the row generator

\[
Q(\theta)=Q_0-BD_{\kappa(\theta)},\qquad
\kappa(\theta)=\sum_jw_j(\theta)\kappa_j,
\]

the probability column and allocation tangents satisfy

\[
p_t=Q^Tp,\qquad
(s_i)_t=Q^Ts_i-BD_{u_i}p,
\quad u_i=\sum_jP_{ji}\kappa_j.
\]

The runner carries both the state term and the direct observable term.  With
`a[0]=kappa`, `a[r+1]=Q a[r]`, `b[0,i]=u[i]`, and

\[
b_{r+1,i}=Qb_{r,i}-BD_{u_i}a_r,
\]

it evaluates

\[
F^{(r)}=p^Ta_r,\qquad
F^{(r)}_{\theta_i}=s_i^Ta_r+p^Tb_{r,i},
\]

where `F=f/B` for positive `B` and denotes the continuous `B=0` limit at the
first homotopy step.  The cusp system and full analytic Jacobian are

\[
H=(F_t,F_{tt},F_{ttt})=0,
\]

\[
DH=\begin{pmatrix}
F_{tt}&F_{t\theta_1}&F_{t\theta_2}\\
F_{ttt}&F_{tt\theta_1}&F_{tt\theta_2}\\
F_{tttt}&F_{ttt\theta_1}&F_{ttt\theta_2}
\end{pmatrix}.
\]

## 5. Cusp homotopy and trust region

Each mesh independently starts at
`(t,theta1,theta2)=(13.30724696053485,0,0)` and follows exactly

```text
B = 0, 0.0025, 0.0050, 0.0075, 0.0100.
```

Every Newton solve is confined to

```text
9 <= t <= 18
||theta||_infinity <= 0.15
min(weight) >= 0.03
```

with at most 12 updates, at most eight deterministic halvings, strict
dimensionless-residual descent, and convergence tolerance `1e-10`.  Failure
at any budget is `HOLD_DISCOVERY`; the schedule, chart, or trust box may not be
changed.

Every serialized homotopy point must remain inside that frozen
time/allocation/simplex trust box and every serialized maximum residual must be
nonnegative.  The terminal cusp snapshot must have budget exactly `0.01`,
positive per-budget density, weights reconstructed from its chart coordinates,
and `density = B * density_per_budget` in its state-law row.  Its model
diagnostics must reconstruct the installed budget, minimum and sum of those
weights, initial-mass error, and physical-installed-budget error.  The same
budget/weight/model and density-law identities apply recursively to fold nodes,
controls, saved scans, and tail rows.

At the `B=0.01` cusp on each mesh, analytic state tangents and the entire
three-by-three cusp Jacobian are compared with centred differences at
allocation steps `(2e-5,1e-5)` and relative-time steps `(2e-5,1e-5)`.  The
smaller-step error must decrease by the frozen factor or enter the `5e-8`
roundoff floor, and maximum normalized disagreement is `1e-6`.

The dimensionless cusp gates are fixed in the manifest.  They include the
three residuals, strict simplex margin, scaled fourth derivative, both
singular values and their ratio for the projected response, the smallest
singular value of the full Jacobian, determinant factorization, survival
identities, killed-generator identity, positivity, initial mass, installed
budget, differential mass balance, and the mixed-jet audit.  A structural
rank or quartic failure is a finite-JSON HOLD, never a relaxed threshold.

The same physical-law checks are evaluated at the positive-`B` cusp, every
accepted fold node, every saved stationary-scan point, every refined root,
and the frozen tail checkpoints `35,50,75,100`.  The numerical thresholds are
unchanged from v2 and frozen as

```text
minimum density                    > 0
minimum survival                   > 0
state negativity tolerance         1e-12
sampled survival increase          1e-12
initial-mass error                  1e-12
installed-budget error              1e-12
S_t + f identity error              1e-9
Q 1 + B kappa identity error        1e-9
differential mass-balance error     1e-9
event-partition closure error       1e-9
```

The v6 factor gate is reconstructed from primitive frozen quantities in both
producer and auditor.  The three spacings must equal their domain lengths
divided by `N`; every patch integral and both initial-factor masses must equal
one within `1e-10`; `contact_area_exact` must equal `pi*0.16^2`; the measured
contact error must be covered by its nonnegative estimate.  Patch, initial,
and contact estimates are at most `1e-10` and may under-cover a reported
discrepancy by at most `5e-13`; both generator row-sum errors are nonnegative
and at most `1e-10`.  One failed factor clears
`finite_factor_diagnostics` and every dependent scientific PASS.

The outer killed-generator diagnostics are no longer trusted summaries.  Each
row serializes midpoint-profile and contact-profile minima, maxima, and sums,
plus the midpoint and relative free-generator diagonal sums.  Producer and
independent auditor reconstruct the two Scharfetter--Gummel traces directly
from `D`, `gamma`, the frozen faces, and `N`, add the periodic transverse trace,
reconstruct the separable killing extrema and sum, and then require

\[
\operatorname{tr}Q
=N^2\operatorname{tr}Q_m+N\operatorname{tr}Q_r
-B\sum\kappa.
\]

The midpoint normalization, contact area, installed budget, and
`Q 1 + B kappa` row-error coverage are independently reconstructed as well.
Every serialized quantity named as an error, residual, singular value,
absolute mismatch, drift, or event mass is an exact native finite `float` and
is nonnegative.  A numerically failed scientific evaluation uses the fixed
finite HOLD schema; it cannot encode failure as a negative norm.

All finite-volume factor diagnostics, the complete 691-row scan, its exact
70-row `0.5`-spaced projection, tail traces, and every
bracketed root with its eligibility reasons are serialized.  The full-scan
minimum density, minimum survival, minimum state component, maximum survival
increase, and maximum differential mass-balance error gate every mesh,
representative control, and comparison-node scan.  Every entry of
`all_bracketed_roots`, including an ineligible refined root, must pass the same
positivity, state, survival, and mass-balance law before its containing row can
pass.  A nonfinite
scientific value becomes a fixed finite `HOLD_CONTROL_EVALUATION` row with
`null` unavailable quantities; it can never reach ranking.

## 6. Remote pair and both fold branches

Stationary roots are isolated on the finite retained window `[0.5,35]` with
spacing `0.05` and exactly 691 scan points on both discovery meshes and refined only inside sign-changing
brackets by the frozen Brent tolerances.  Eligibility requires positive
density, the relative-density floor, scaled root residual `<=1e-8`, and
absolute scaled curvature `>=0.05`.  The full-scan maximum per-budget density
is serialized as the reference for the density rule.  Producer and auditor
reconstruct all 691 grid times, the exact 70-row stride projection, maximum,
minima and error aggregates, every sign-change/zero bracket, endpoint signs,
root type, all eligibility flags and ordered reasons, duplicates, minimum
separation, topology, bracket-grid alignment, spacing, and point count instead
of trusting self-reported flags.  This is complete for the frozen sampled
grid; it is not a theorem excluding an even-multiplicity root wholly inside a
single `0.05` interval.

A remote pair is an ordered `maximum-minimum` pair on one side of the cusp,
outside the `0.25` cusp neighborhood, with separation at least `0.25`.  The
finite window and filters may not expand after a failure.

Both folds start from the analytic predictors at `tau=-0.10,+0.10`:

\[
R_1\eta=F_{tttt}\tau^3/3,\qquad
R_2\eta=-F_{tttt}\tau^2/2.
\]

Each seed is corrected at fixed time, then continued by pseudo-arclength.  The
initial step is `0.05`, bounded by `[0.025,0.20]`, with the deterministic
iteration-count adaptation written in the manifest.  One half-step retry is
allowed after failure.  A branch stops at `|t-t_c|=2`, `min(weight)=0.03`, or
24 accepted noncusp nodes.  For declared sign `s` it must have at least six
nodes and reach `s(t-t_c)>=0.75`; absolute reach on the wrong side is
ineligible.  Three distinct comparison indices are selected without
replacement on the declared side at signed offsets `0.25,0.50,0.75` by the
frozen mismatch/residual/index tie-break.  Each absolute offset mismatch must
be at most `0.125`.  Both branches must keep their orientation and pass
residual, third-derivative, physical-law, and rank gates.  The bounded
stationary-root procedure is rerun at all six comparison nodes.  The pair
identity is frozen at the cusp scan and contains the signed side, pair type,
selected global eligible-root indices, and originating bracket indices.  Every
eligible root is continued by fixed global ordinal, type, signed side, origin
bracket, and order-preserving predecessor/successor.  Its time may drift by at
most `1.0` between adjacent comparison scans.  Root birth, death, crossing,
unmatched order, selected-pair replacement, or excess adjacent drift is
`HOLD_BRANCH`.  The `1.0` cap is a result-blind design value frozen before
meshes 65 or 97 and cannot be adjusted from a scientific trace.

## 7. Finite phase search

Only after both low-mesh cusps pass, the mesh-97 cusp defines the common chart
centre.  It is serialized and cross-linked to the mesh-97 cusp theta.  Every
candidate is checked directly against the formula below with frozen absolute
tolerance `5e-13`; recovered-centre subtraction and bitwise equality are not
used.  The runner enumerates exactly 32 controls:

\[
\theta=\theta_c^{97}+r d_k,
\quad r\in\{0.02,0.05,0.09,0.13\},
\]

where the eight printed direction vectors in the manifest are the compass and
diagonal directions.  Invalid simplex/trust controls are discarded, not
replaced.

All geometrically eligible controls are screened on mesh 65.  Any missing or
nonfinite eligible screen makes the entire phase HOLD; already successful
controls cannot hide the missing row.  For each retained-window maximum count
`1`, `2`, and `3`, at most three controls advance to mesh 97, and any missing
selected mesh-97 evaluation also makes the entire phase HOLD.  Ranking uses
exactly the ordered terms

```text
peak_ratio
valley_ratio
absolute_scaled_curvature
event_basin_mass
```

For a lower bound the margin is `value/lower_bound - 1`; for an upper bound it
is `(upper_bound-value)/(1-upper_bound)`.  The score is the minimum of those
four margins.  Root residual is an eligibility gate only and is not a ranking
term.  The physical weight vector is the final lexicographic tie-break.  The
representative for each count maximizes its worst score across the two meshes.
Required law gates are
alternating retained topology, endpoint signs, root residual, curvature,
peak ratio, valley ratio, and every valley-partitioned event mass by `T=100`.
If any count is absent, the result is HOLD.  Radius expansion, a new chart,
or extra candidates are forbidden.

## 8. Execution and atomic publication

The manifest pins the runner, ordinary, Round-50, Round-61, Round-74,
converted Round-80, and Round-85 repair tests, this protocol, the Stage-A
algebra scaffold, and the design/audit chain including Rounds 50, 61, 74, 80,
and the independent Round-84 failure report, the
positive-`B` v2 family manifest/protocol/producer, and finite-volume
dependencies, including the directly imported
`code/continuum_observable_four_patch.py`.  All paths are report-relative lexical regular files.  Every
pin and the manifest itself are captured through `lstat`, `O_NOFOLLOW`, and a
stable descriptor; initial and final device/inode/mode/size/mtime/hash metadata
and exact bytes must agree.  The formal and audit windows have an explicit
no-concurrent-writer/no-OneDrive-replacement contract.  A detected rewrite,
relink, replace, or restore is operational failure with no publication.
Formal commands require the manifest SHA-256 supplied externally.  The formal
parent itself, not merely its children, must start with Python `-I -S -B` so that
neither `sitecustomize` nor a user/site `.pth` file can execute before the
runner and no new bytecode cache can be written.  Because `-B` does not prevent
CPython from reading an existing valid `pyc`, the frozen provenance hashes the
exact NumPy, SciPy, `numpy.libs`, and `scipy.libs` import trees, including every
`__pycache__/*.pyc`, every unrecorded regular file, and every symlink target and
basic mode/size metadata.  The wheel `RECORD` rows are independently parsed and
rehashed from actual bytes; their native-extension subset has its own closure.
The only non-stdlib path added by the bootstrap is the absolute
repository `.venv` `site-packages` directory. The runner verifies that path,
`isolated`, `no_site`, `ignore_environment`, `safe_path`, and active Python
hash randomization before any formal work. `-I` deliberately ignores
`PYTHONHASHSEED`; v6 therefore makes no false fixed-hash claim. Every
set/dict-derived sequence is explicitly sorted before order-sensitive
scientific, tie-break, or serialized use, and the two complete replicas must
still be byte-identical. Before `runpy` can import NumPy, the stdlib-only
bootstrap captures the manifest and runner through stable `O_NOFOLLOW`
descriptors, checks the externally supplied manifest hash and manifest-pinned
runner bytes, verifies the exact Python executable/framework and full stdlib
tree (including existing `pyc` bytes and symlink metadata), and checks both
distribution/import-tree closures. It also rehashes every declared non-system
Mach-O row, independently reconstructs install names, lexical/resolved paths,
sizes, hashes, `LC_RPATH`s, and recursively resolved load commands, and requires
the currently mapped pre-third-party phase to be an exact set. The future phase
sets must be sorted and monotone; they are not accepted as observations merely
because they appear in the manifest. After import, the producer and independent
auditor each execute their separately implemented staged direct-import probe,
rebuild four exact phases in the real order—bootstrap pre-third-party, pure
runner post-import, post-manifest-validation, and full-stack post-import—and
rebuild the complete bounded closure from bytes. The transition from 93 pure
runner images to 94 post-validation images is explicitly attributed to
`signed_dyld_cache_provenance.platform.mac_ver`, whose XML parser loads the one
frozen `pyexpat` image; it is not folded into the pure runner phase. The full
stack contains those 94 images plus the four later local-stack additions, for
98 images. Each formal checkpoint requires exact equality with its matching
phase.
Thus the auditor independently rebuilds the external native rows instead of
trusting them. The bootstrap also verifies every arm64e dyld subcache with its
signed CodeDirectory hash through a byte-pinned `/usr/bin/codesign`. System
`/System/Library` and `/usr/lib` dependencies are signed-cache leaves. After
import, both implementations also bind the exact NumPy/SciPy versions and
origins and the complete NumPy build configuration, including the Accelerate
BLAS/LAPACK choice.

The bootstrap necessarily imports `hashlib`, `json`, `os`, `runpy`, `stat`,
`sys`, and the stdlib machinery used to enumerate dyld images before it can
verify the stdlib closure. Therefore the interpreter, those bootstrap modules,
the hashing primitive (including its loaded `libcrypto`), and the dyld
enumerator are an explicit root of
trust.  The stdlib closure is a reproducibility attestation and drift detector,
not a claim to prevent an already hostile interpreter/stdlib.  This bounded
claim is distinct from the reproducibility witness: every actually mapped
non-system image, including probe-induced `ctypes/_ctypes`, plus every
recursive non-system dependency is nevertheless frozen and independently
rebuilt. This is drift/provenance control under the no-concurrent-writer
contract, not malicious same-UID prevention. The
following is the single authorized command, run from the repository root:

```bash
ROOT=$(pwd -P)
PY="$ROOT/.venv/bin/python"
RUNNER="$ROOT/research/reports/encounter_multimodal_prr/code/positive_b_allocation_cusp_discovery.py"
SITE="$ROOT/.venv/lib/python3.12/site-packages"
BOOTSTRAP='import ctypes
import hashlib
import importlib
import json
import os
import runpy
import stat
import sys

runner, site_packages, *arguments = sys.argv[1:]
if sys.flags.isolated != 1 or sys.flags.no_site != 1 or not sys.dont_write_bytecode:
    raise SystemExit("formal bootstrap requires -I -S -B")
if not os.path.isabs(runner) or not os.path.isabs(site_packages):
    raise SystemExit("formal bootstrap paths must be absolute")
if "sitecustomize" in sys.modules or "usercustomize" in sys.modules:
    raise SystemExit("formal bootstrap loaded a customization module")

def stable_bytes(path):
    before = os.lstat(path)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise SystemExit("formal bootstrap input is not a regular file")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(descriptor)
        chunks = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        closed = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    after = os.lstat(path)
    identities = {
        (item.st_dev, item.st_ino, item.st_mode, item.st_size, item.st_mtime_ns)
        for item in (before, opened, closed, after)
    }
    if len(identities) != 1:
        raise SystemExit("formal bootstrap input changed during capture")
    payload = b"".join(chunks)
    if len(payload) != before.st_size:
        raise SystemExit("formal bootstrap input was read short")
    return payload

def closure_digest(rows):
    digest = hashlib.sha256()
    for name, file_hash in sorted(rows):
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()

def tree_closure(root, file_hash_cache=None):
    try:
        root_metadata = os.lstat(root)
    except FileNotFoundError:
        return {
            "present": False,
            "entry_count": 0,
            "regular_file_count": 0,
            "pyc_file_count": 0,
            "symlink_count": 0,
            "closure_sha256": closure_digest([]),
        }
    if stat.S_ISLNK(root_metadata.st_mode) or not stat.S_ISDIR(root_metadata.st_mode):
        raise SystemExit("formal bootstrap import-tree root is not a lexical directory")
    cache = file_hash_cache if file_hash_cache is not None else {}
    rows = []
    regular_count = 0
    pyc_count = 0
    symlink_count = 0
    for directory, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
        kept_directories = []
        for name in sorted(directory_names):
            path = os.path.join(directory, name)
            metadata = os.lstat(path)
            if stat.S_ISLNK(metadata.st_mode):
                relative = os.path.relpath(path, root).replace(os.sep, "/")
                rows.append(
                    (
                        relative,
                        f"L:{metadata.st_mode}:{metadata.st_size}:{os.readlink(path)}",
                    )
                )
                symlink_count += 1
                continue
            if not stat.S_ISDIR(metadata.st_mode):
                raise SystemExit("formal bootstrap import tree contains a non-directory")
            kept_directories.append(name)
        directory_names[:] = kept_directories
        for name in sorted(file_names):
            path = os.path.join(directory, name)
            metadata = os.lstat(path)
            if stat.S_ISLNK(metadata.st_mode):
                relative = os.path.relpath(path, root).replace(os.sep, "/")
                rows.append(
                    (
                        relative,
                        f"L:{metadata.st_mode}:{metadata.st_size}:{os.readlink(path)}",
                    )
                )
                symlink_count += 1
                continue
            if not stat.S_ISREG(metadata.st_mode):
                raise SystemExit("formal bootstrap import tree contains a special file")
            relative = os.path.relpath(path, root).replace(os.sep, "/")
            file_hash = cache.get(path)
            if file_hash is None:
                file_hash = hashlib.sha256(stable_bytes(path)).hexdigest()
                cache[path] = file_hash
            rows.append(
                (
                    relative,
                    f"F:{metadata.st_mode}:{metadata.st_size}:{file_hash}",
                )
            )
            regular_count += 1
            pyc_count += int(name.endswith(".pyc"))
    return {
        "present": True,
        "entry_count": len(rows),
        "regular_file_count": regular_count,
        "pyc_file_count": pyc_count,
        "symlink_count": symlink_count,
        "closure_sha256": closure_digest(rows),
    }

def lexical_regular_under(root, path):
    root = os.path.abspath(root)
    path = os.path.abspath(os.path.normpath(path))
    if os.path.commonpath((root, path)) != root or path == root:
        raise SystemExit("formal bootstrap package path escapes the frozen venv")
    current = root
    parts = os.path.relpath(path, root).split(os.sep)
    for index, part in enumerate(parts):
        current = os.path.join(current, part)
        metadata = os.lstat(current)
        if stat.S_ISLNK(metadata.st_mode):
            raise SystemExit("formal bootstrap package path contains a symlink")
        expected = stat.S_ISREG if index == len(parts) - 1 else stat.S_ISDIR
        if not expected(metadata.st_mode):
            raise SystemExit("formal bootstrap package path has the wrong file type")
    return stable_bytes(path)

if arguments.count("--expected-manifest-sha256") != 1:
    raise SystemExit("formal bootstrap requires one external manifest hash")
hash_index = arguments.index("--expected-manifest-sha256")
if hash_index + 1 >= len(arguments):
    raise SystemExit("formal bootstrap manifest hash value is missing")
expected_manifest_hash = arguments[hash_index + 1]
report = os.path.dirname(os.path.dirname(runner))
repository = os.path.realpath(os.path.join(os.path.dirname(runner), "../../../.."))
manifest_path = os.path.join(
    report, "artifacts", "data", "positive_b_allocation_cusp_discovery_manifest.json"
)
manifest_bytes = stable_bytes(manifest_path)
if hashlib.sha256(manifest_bytes).hexdigest() != expected_manifest_hash:
    raise SystemExit("formal bootstrap external manifest hash mismatch")
manifest = json.loads(manifest_bytes)
provenance = manifest.get("runtime_provenance")
if not isinstance(provenance, dict) or provenance.get("contract") != "bounded_runtime_closure_v2":
    raise SystemExit("formal bootstrap runtime provenance is missing")
runner_pin = manifest["pinned_files"]["runner"]
expected_runner = os.path.realpath(os.path.join(report, runner_pin["path"]))
runner_bytes = stable_bytes(runner)
if (
    os.path.realpath(runner) != expected_runner
    or hashlib.sha256(runner_bytes).hexdigest() != runner_pin["sha256"]
):
    raise SystemExit("formal bootstrap runner pin mismatch")
expected_site = os.path.realpath(
    os.path.join(
        repository,
        ".venv",
        "lib",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
        "site-packages",
    )
)
if os.path.realpath(site_packages) != expected_site or not os.path.isdir(expected_site):
    raise SystemExit("formal bootstrap repository site-packages mismatch")

python_provenance = provenance.get("python")
if not isinstance(python_provenance, dict):
    raise SystemExit("formal bootstrap Python provenance is malformed")
real_executable = os.path.realpath(sys.executable)
expected_stdlib = os.path.realpath(
    os.path.join(
        sys.base_prefix,
        "lib",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
    )
)
if (
    python_provenance.get("version") != sys.version
    or python_provenance.get("cache_tag") != sys.implementation.cache_tag
    or python_provenance.get("invocation_path") != os.path.abspath(sys.executable)
    or python_provenance.get("real_executable_path") != real_executable
    or python_provenance.get("stdlib_root") != expected_stdlib
):
    raise SystemExit("formal bootstrap Python identity mismatch")
if (
    hashlib.sha256(stable_bytes(real_executable)).hexdigest()
    != python_provenance.get("real_executable_sha256")
):
    raise SystemExit("formal bootstrap Python executable hash mismatch")
if tree_closure(expected_stdlib) != python_provenance.get("stdlib_closure"):
    raise SystemExit("formal bootstrap stdlib closure mismatch")
framework_files = python_provenance.get("framework_files")
if not isinstance(framework_files, dict) or not framework_files:
    raise SystemExit("formal bootstrap Python framework closure is malformed")
for path, expected_hash in framework_files.items():
    if not os.path.isabs(path) or hashlib.sha256(stable_bytes(path)).hexdigest() != expected_hash:
        raise SystemExit("formal bootstrap Python framework hash mismatch")

venv_root = os.path.realpath(os.path.join(repository, ".venv"))
if (
    provenance.get("venv_root") != venv_root
    or provenance.get("site_packages") != expected_site
):
    raise SystemExit("formal bootstrap frozen venv identity mismatch")

import csv
import io

def distribution_closure(record_path, file_hash_cache):
    record_bytes = lexical_regular_under(venv_root, record_path)
    try:
        records = list(csv.reader(io.StringIO(record_bytes.decode("utf-8"), newline="")))
    except (UnicodeDecodeError, csv.Error) as error:
        raise SystemExit("formal bootstrap package RECORD is malformed") from error
    rows = []
    native_rows = []
    seen = set()
    for record in records:
        if len(record) != 3 or not record[0]:
            raise SystemExit("formal bootstrap package RECORD row is malformed")
        path = os.path.abspath(os.path.normpath(os.path.join(expected_site, record[0])))
        relative = os.path.relpath(path, venv_root).replace(os.sep, "/")
        if relative in seen:
            raise SystemExit("formal bootstrap package RECORD contains a duplicate path")
        seen.add(relative)
        file_hash = file_hash_cache.get(path)
        if file_hash is None:
            file_hash = hashlib.sha256(lexical_regular_under(venv_root, path)).hexdigest()
            file_hash_cache[path] = file_hash
        rows.append((relative, file_hash))
        if relative.endswith((".so", ".dylib", ".pyd", ".dll")):
            native_rows.append((relative, file_hash))
    return {
        "record_file_count": len(rows),
        "record_sha256": hashlib.sha256(record_bytes).hexdigest(),
        "record_closure_sha256": closure_digest(rows),
        "native_extension_count": len(native_rows),
        "native_extension_closure_sha256": closure_digest(native_rows),
    }

distributions = provenance.get("distributions")
if not isinstance(distributions, dict) or set(distributions) != {"numpy", "scipy"}:
    raise SystemExit("formal bootstrap distribution provenance is malformed")
for distribution_name, distribution in distributions.items():
    record_path = distribution.get("record_path")
    file_hash_cache = {}
    observed_trees = {}
    expected_trees = distribution.get("import_tree_closures")
    if (
        not isinstance(expected_trees, dict)
        or set(expected_trees) != {distribution_name, f"{distribution_name}.libs"}
    ):
        raise SystemExit("formal bootstrap import-tree provenance is malformed")
    for root_name, expected_tree in expected_trees.items():
        if not isinstance(root_name, str) or not isinstance(expected_tree, dict):
            raise SystemExit("formal bootstrap import-tree row is malformed")
        root_path = expected_tree.get("path")
        expected_root_path = os.path.join(expected_site, root_name)
        if not isinstance(root_path, str) or root_path != expected_root_path:
            raise SystemExit("formal bootstrap import-tree path is malformed")
        observed_trees[root_name] = {"path": root_path, **tree_closure(root_path, file_hash_cache)}
    if observed_trees != expected_trees:
        raise SystemExit("formal bootstrap import-tree exact-set closure mismatch")
    expected_closure = {
        key: distribution.get(key)
        for key in (
            "record_file_count",
            "record_sha256",
            "record_closure_sha256",
            "native_extension_count",
            "native_extension_closure_sha256",
        )
    }
    if (
        not isinstance(record_path, str)
        or distribution_closure(record_path, file_hash_cache) != expected_closure
    ):
        raise SystemExit("formal bootstrap distribution RECORD closure mismatch")

system_native = provenance.get("system_native")
if not isinstance(system_native, dict):
    raise SystemExit("formal bootstrap system-native provenance is malformed")
codesign_tool = system_native.get("codesign_tool")
if (
    not isinstance(codesign_tool, dict)
    or codesign_tool.get("path") != "/usr/bin/codesign"
    or hashlib.sha256(stable_bytes(codesign_tool["path"])).hexdigest()
    != codesign_tool.get("sha256")
):
    raise SystemExit("formal bootstrap codesign tool mismatch")

import subprocess

cache_rows = system_native.get("dyld_cache_code_directories")
if not isinstance(cache_rows, list) or not cache_rows:
    raise SystemExit("formal bootstrap dyld cache provenance is malformed")
cache_root = system_native.get("dyld_cache_root")
expected_cache_paths = {row.get("path") for row in cache_rows if isinstance(row, dict)}
observed_cache_paths = set()
cache_prefix = "dyld_shared_cache_arm64e"
for name in os.listdir(cache_root):
    suffix = name[len(cache_prefix):] if name.startswith(cache_prefix) else ""
    if name == cache_prefix or (
        suffix.startswith(".") and suffix[1:].split(".", 1)[0].isdigit()
    ):
        observed_cache_paths.add(os.path.join(cache_root, name))
if observed_cache_paths != expected_cache_paths:
    raise SystemExit("formal bootstrap dyld cache file set mismatch")
codesign_environment = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}
for row in cache_rows:
    path = row.get("path")
    before = os.lstat(path)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise SystemExit("formal bootstrap dyld cache is not a regular file")
    verified = subprocess.run(
        [codesign_tool["path"], "--verify", "--strict", path],
        env=codesign_environment,
        check=False,
        capture_output=True,
        text=True,
    )
    described = subprocess.run(
        [codesign_tool["path"], "-dvvv", path],
        env=codesign_environment,
        check=False,
        capture_output=True,
        text=True,
    )
    after = os.lstat(path)
    identity_before = (before.st_dev, before.st_ino, before.st_mode, before.st_size, before.st_mtime_ns)
    identity_after = (after.st_dev, after.st_ino, after.st_mode, after.st_size, after.st_mtime_ns)
    full_hashes = [
        line.split("=", 1)[1]
        for line in (described.stdout + described.stderr).splitlines()
        if line.startswith("CandidateCDHashFull sha256=")
    ]
    if (
        verified.returncode != 0
        or described.returncode != 0
        or identity_before != identity_after
        or row.get("size") != before.st_size
        or full_hashes != [row.get("candidate_cdhash_full_sha256")]
    ):
        raise SystemExit("formal bootstrap signed dyld cache attestation mismatch")

non_system_native = provenance.get("non_system_native")
native_phases = (
    "bootstrap_pre_third_party",
    "runner_post_import",
    "post_manifest_validation",
    "full_stack_post_import",
)
system_prefixes = (
    "/System/Library/",
    "/usr/lib/",
    "/System/Volumes/Preboot/Cryptexes/OS/System/Library/",
)
if (
    not isinstance(non_system_native, dict)
    or non_system_native.get("contract") != "bounded_non_system_macho_closure_v1"
    or non_system_native.get("threat_boundary")
    != "reproducibility_witness_not_malicious_same_uid_prevention"
    or non_system_native.get("bootstrap_root_of_trust_includes_hash_primitive") is not True
    or non_system_native.get("probe_induced_images_included") != ["ctypes", "_ctypes"]
    or non_system_native.get("system_leaf_prefixes") != list(system_prefixes)
):
    raise SystemExit("formal bootstrap non-system native provenance is malformed")

def is_system_native(path):
    return any(path.startswith(prefix) for prefix in system_prefixes)

def loaded_non_system_images():
    dyld = ctypes.CDLL(None)
    dyld._dyld_image_count.restype = ctypes.c_uint32
    dyld._dyld_get_image_name.argtypes = [ctypes.c_uint32]
    dyld._dyld_get_image_name.restype = ctypes.c_char_p
    rows = {}
    for index in range(int(dyld._dyld_image_count())):
        encoded = dyld._dyld_get_image_name(index)
        if not encoded:
            continue
        lexical = os.fsdecode(encoded)
        if not os.path.isabs(lexical):
            raise SystemExit("formal bootstrap dyld image path is not absolute")
        resolved = os.path.realpath(lexical)
        if is_system_native(lexical) or is_system_native(resolved):
            continue
        row = {"lexical_path": lexical, "resolved_path": resolved}
        previous = rows.setdefault(resolved, row)
        if previous != row:
            raise SystemExit("formal bootstrap dyld image alias changed")
    return [rows[key] for key in sorted(rows)]

phase_images = non_system_native.get("phase_images")
if not isinstance(phase_images, dict) or set(phase_images) != set(native_phases):
    raise SystemExit("formal bootstrap native phase map is malformed")
phase_sets = {}
previous_phase = set()
for phase in native_phases:
    phase_rows = phase_images.get(phase)
    if not isinstance(phase_rows, list) or not phase_rows:
        raise SystemExit("formal bootstrap native phase is empty")
    resolved_order = []
    for row in phase_rows:
        if (
            not isinstance(row, dict)
            or set(row) != {"lexical_path", "resolved_path"}
            or not isinstance(row.get("lexical_path"), str)
            or not isinstance(row.get("resolved_path"), str)
            or not os.path.isabs(row["lexical_path"])
            or not os.path.isabs(row["resolved_path"])
            or os.path.realpath(row["lexical_path"]) != row["resolved_path"]
            or is_system_native(row["lexical_path"])
            or is_system_native(row["resolved_path"])
        ):
            raise SystemExit("formal bootstrap native phase row is malformed")
        resolved_order.append(row["resolved_path"])
    if resolved_order != sorted(set(resolved_order)):
        raise SystemExit("formal bootstrap native phase is not uniquely sorted")
    phase_sets[phase] = set(resolved_order)
    if not previous_phase.issubset(phase_sets[phase]):
        raise SystemExit("formal bootstrap native phases are not monotone")
    previous_phase = phase_sets[phase]
if loaded_non_system_images() != phase_images["bootstrap_pre_third_party"]:
    raise SystemExit("formal bootstrap pre-third-party native image set changed")

transition_causes = non_system_native.get("phase_transition_causes")
transition_added = [
    row
    for row in phase_images["post_manifest_validation"]
    if row not in phase_images["runner_post_import"]
]
if (
    not isinstance(transition_causes, dict)
    or set(transition_causes) != {"post_manifest_validation"}
    or transition_causes["post_manifest_validation"]
    != {
        "operation": "signed_dyld_cache_provenance.platform.mac_ver",
        "added_images": transition_added,
    }
    or len(transition_added) != 1
    or not os.path.basename(transition_added[0]["resolved_path"]).startswith("pyexpat.")
):
    raise SystemExit("formal bootstrap native phase-transition cause changed")

main_image = non_system_native.get("main_executable_image")
if (
    not isinstance(main_image, dict)
    or set(main_image) != {"lexical_path", "resolved_path"}
    or main_image not in phase_images["bootstrap_pre_third_party"]
):
    raise SystemExit("formal bootstrap main native image is malformed")
native_executable = main_image["resolved_path"]
otool = non_system_native.get("otool")
if (
    not isinstance(otool, dict)
    or set(otool) != {"path", "sha256"}
    or otool.get("path") != "/usr/bin/otool"
    or hashlib.sha256(stable_bytes(otool["path"])).hexdigest() != otool.get("sha256")
):
    raise SystemExit("formal bootstrap otool provenance mismatch")

def macho_commands(path):
    completed = subprocess.run(
        [otool["path"], "-l", path],
        env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit("formal bootstrap otool inspection failed")
    lines = completed.stdout.splitlines()
    install_names = []
    rpaths = []
    dependencies = []
    load_commands = {
        "LC_LOAD_DYLIB",
        "LC_LOAD_WEAK_DYLIB",
        "LC_REEXPORT_DYLIB",
        "LC_LOAD_UPWARD_DYLIB",
    }
    for index, line in enumerate(lines):
        command = line.strip()
        if command == "cmd LC_ID_DYLIB":
            for candidate in lines[index + 1 : index + 6]:
                item = candidate.strip()
                if item.startswith("name "):
                    install_names.append(item[5:].split(" (offset ", 1)[0])
                    break
        elif command.removeprefix("cmd ") in load_commands:
            for candidate in lines[index + 1 : index + 6]:
                item = candidate.strip()
                if item.startswith("name "):
                    dependencies.append(item[5:].split(" (offset ", 1)[0])
                    break
        elif command == "cmd LC_RPATH":
            for candidate in lines[index + 1 : index + 6]:
                item = candidate.strip()
                if item.startswith("path "):
                    rpaths.append(item[5:].split(" (offset ", 1)[0])
                    break
    unique_install_names = sorted(set(install_names))
    if len(unique_install_names) > 1:
        raise SystemExit("formal bootstrap native install names disagree")
    return (
        unique_install_names[0] if unique_install_names else None,
        list(dict.fromkeys(rpaths)),
        sorted(set(dependencies)),
    )

def expand_anchor(value, loader):
    if value == "@loader_path":
        return os.path.dirname(loader)
    if value.startswith("@loader_path/"):
        return os.path.join(os.path.dirname(loader), value[len("@loader_path/") :])
    if value == "@executable_path":
        return os.path.dirname(native_executable)
    if value.startswith("@executable_path/"):
        return os.path.join(
            os.path.dirname(native_executable), value[len("@executable_path/") :]
        )
    if os.path.isabs(value):
        return value
    raise SystemExit("formal bootstrap unsupported Mach-O path anchor")

def resolve_dependency(install_name, loader, rpaths):
    if is_system_native(install_name):
        return {
            "install_name": install_name,
            "classification": "system_dyld_cache",
            "lexical_path": install_name,
            "resolved_path": None,
        }
    if install_name.startswith("@rpath/"):
        suffix = install_name[len("@rpath/") :]
        candidates = []
        for rpath in rpaths:
            candidate = os.path.abspath(
                os.path.normpath(os.path.join(expand_anchor(rpath, loader), suffix))
            )
            if os.path.lexists(candidate):
                candidates.append(candidate)
        if not candidates:
            raise SystemExit("formal bootstrap unresolved @rpath dependency")
        lexical = candidates[0]
    else:
        lexical = os.path.abspath(os.path.normpath(expand_anchor(install_name, loader)))
    resolved = os.path.realpath(lexical)
    if is_system_native(lexical) or is_system_native(resolved):
        return {
            "install_name": install_name,
            "classification": "system_dyld_cache",
            "lexical_path": lexical,
            "resolved_path": None,
        }
    if not os.path.lexists(lexical):
        raise SystemExit("formal bootstrap non-system dependency is absent")
    return {
        "install_name": install_name,
        "classification": "non_system",
        "lexical_path": lexical,
        "resolved_path": resolved,
    }

image_rows = non_system_native.get("images")
if (
    not isinstance(image_rows, list)
    or non_system_native.get("closure_image_count") != len(image_rows)
    or not image_rows
):
    raise SystemExit("formal bootstrap native closure rows are malformed")
expected_image_keys = {
    "resolved_path",
    "lexical_paths",
    "install_name",
    "size",
    "sha256",
    "rpaths",
    "dependencies",
    "actual_loaded_phases",
}
row_map = {}
observed_aliases = {}
observed_metadata = {}
for phase in native_phases:
    for row in phase_images[phase]:
        observed_aliases.setdefault(row["resolved_path"], set()).add(row["lexical_path"])
for row in image_rows:
    if (
        not isinstance(row, dict)
        or set(row) != expected_image_keys
        or not isinstance(row.get("resolved_path"), str)
        or row["resolved_path"] in row_map
        or not os.path.isabs(row["resolved_path"])
        or is_system_native(row["resolved_path"])
    ):
        raise SystemExit("formal bootstrap native closure row is malformed")
    path = row["resolved_path"]
    payload = stable_bytes(path)
    if len(payload) != row.get("size") or hashlib.sha256(payload).hexdigest() != row.get("sha256"):
        raise SystemExit("formal bootstrap native image bytes changed")
    install_name, rpaths, raw_dependencies = macho_commands(path)
    dependencies = sorted(
        [resolve_dependency(name, path, rpaths) for name in raw_dependencies],
        key=lambda item: (
            item["install_name"],
            item["lexical_path"],
            item["resolved_path"] or "",
        ),
    )
    for dependency in dependencies:
        if dependency["resolved_path"] is not None:
            observed_aliases.setdefault(dependency["resolved_path"], set()).add(
                dependency["lexical_path"]
            )
    actual_phases = [phase for phase in native_phases if path in phase_sets[phase]]
    observed_metadata[path] = {
        "install_name": install_name,
        "rpaths": rpaths,
        "dependencies": dependencies,
        "actual_loaded_phases": actual_phases,
    }
    row_map[path] = row
if list(row_map) != sorted(row_map):
    raise SystemExit("formal bootstrap native closure is not path-sorted")
for path, row in row_map.items():
    aliases = row.get("lexical_paths")
    if (
        not isinstance(aliases, list)
        or aliases != sorted(set(aliases))
        or aliases != sorted(observed_aliases.get(path, {path}))
        or any(os.path.realpath(alias) != path for alias in aliases)
        or row.get("install_name") != observed_metadata[path]["install_name"]
        or row.get("rpaths") != observed_metadata[path]["rpaths"]
        or row.get("dependencies") != observed_metadata[path]["dependencies"]
        or row.get("actual_loaded_phases") != observed_metadata[path]["actual_loaded_phases"]
    ):
        raise SystemExit("formal bootstrap native image graph changed")
    for dependency in row["dependencies"]:
        target = dependency["resolved_path"]
        if target is not None and target not in row_map:
            raise SystemExit("formal bootstrap native dependency escapes the closure")
reachable = set(phase_sets["full_stack_post_import"])
pending = sorted(reachable)
while pending:
    path = pending.pop(0)
    if path not in row_map:
        raise SystemExit("formal bootstrap loaded native image is absent from closure")
    for dependency in row_map[path]["dependencies"]:
        target = dependency["resolved_path"]
        if target is not None and target not in reachable:
            reachable.add(target)
            pending.append(target)
            pending.sort()
if reachable != set(row_map):
    raise SystemExit("formal bootstrap native closure contains unreachable rows")
encoded_image_rows = json.dumps(
    image_rows, allow_nan=False, separators=(",", ":"), sort_keys=True
).encode("utf-8")
if hashlib.sha256(encoded_image_rows).hexdigest() != non_system_native.get("closure_sha256"):
    raise SystemExit("formal bootstrap native closure digest changed")

sys.path.append(expected_site)
sys.argv = [runner, *arguments]
runpy.run_path(runner, run_name="__main__")
'
env -i HOME="$HOME" PATH="$PATH" LANG="${LANG:-C}" TMPDIR="${TMPDIR:-/tmp}" \
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  "$PY" -I -S -B -c "$BOOTSTRAP" "$RUNNER" "$SITE" \
  --execute-frozen \
  --expected-manifest-sha256 <frozen-sha256>
```

Direct `python RUNNER --execute-frozen` invocation is rejected.  The parent
uses the same `python -I -S -B` absolute bootstrap for both replicas and passes
only an explicit harmless environment allowlist plus the frozen thread
variables; `PYTHONPATH`, `PYTHONHOME`, `PYTHONSTARTUP`, `PYTHONUSERBASE`, and
`PYTHONHASHSEED`
are absent, as are every `DYLD_*` and `LD_*` native-loader variable.  The four
local runtime modules are executed from code compiled
from the exact bytes captured through their manifest-pinned stable file
descriptors, bound to their absolute paths, and re-attested before reuse.
Preloaded or substituted `sys.modules` entries are forbidden.
The pinned legacy Stage-A dry-run scaffold imports its bridge lazily, so merely
collecting its tests cannot preload those four formal runtime names.  The
converted Round-80 regression checks both halves: collection remains clean,
while an explicitly preloaded same-name module is still rejected fail-closed.

Before the first child starts, all five lexical paths below and both deterministic
promotion staging paths must be absent:

```text
artifacts/data/positive_b_allocation_cusp_discovery_result.json
artifacts/data/positive_b_allocation_cusp_discovery_reproducibility.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_1.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.replica_2.json
artifacts/data/positive_b_allocation_cusp_discovery_independent_audit.json
artifacts/data/.positive_b_allocation_cusp_discovery_result.json.staging
artifacts/data/.positive_b_allocation_cusp_discovery_reproducibility.json.staging
```

No canonical result, evidence, or audit artifact is silently deleted.  Hidden
replicas created by this invocation are removed only after their captured
bytes have been compared or after a logged operational failure.  The
reproducibility record serializes this exact five-path pre-run absence boundary.

Immediately before and after every child, the parent revalidates both staging
paths and the exact allowed five-path set: empty at replica one, and only the
first owned replica at replica two.  A stage or canonical/audit collision
introduced by child one aborts before child two.  These launch boundaries are
serialized in the reproducibility evidence.

The public entrypoint launches exactly two complete sequential subprocess
replicas under fixed one-thread BLAS/OpenMP settings, isolated per-process
Python hash randomization, explicit order canonicalization, and a
pinned/restored NumPy seed. The FV dependencies are descriptor-bound only after
the formal pin snapshot.  Each replica revalidates the complete metadata-and-
byte snapshot before and after its calculation and after writing its hidden result;
the parent repeats the full snapshot after each child and before/after
promotion.  Canonical promotion requires byte-identical canonical JSON,
consistent PASS/HOLD exit codes, and an exact v6 result validator. That
validator recursively checks exact native keys/types/cardinalities and algebra
for homotopy, cusp, scans, every bracketed root, branches, comparison scans,
controls, phase, PASS, HOLD, and not-run variants.  It reconstructs candidate
generation, advancement order, representative membership, mandatory false
claims, limitations, and start/end pin snapshots.  Duplicate-key or
noncanonical replica JSON is rejected before promotion.

Within each replica, the fixed seven-cell explicit-CSR action preflight runs
first.  If it fails, neither 65 nor 97 is built and both fixed-shape rows read
`NOT_RUN_AFTER_PREFLIGHT_HOLD`.  Otherwise meshes 65 and 97 are built and run
sequentially; mesh 97 is not built if mesh 65 has already produced a structural
HOLD.  The result and reproducibility evidence are written to hidden staging
files, flushed with `fsync`, and atomically installed by no-replace hard-link
creation.  After both directory
syncs the exact canonical and evidence bytes are reread.  Byte drift or pin
drift removes and syncs both destinations before raising.  Existing canonical
outputs are append-only and cannot be overwritten.  The independent auditor
records the device/inode it creates and rolls back only that owned inode; an
output introduced or replaced by another writer is never silently deleted.

Every scientific failure is serialized as `HOLD_DISCOVERY` with fixed-shape
mesh rows and `null` for unavailable structures.  An operational exception
publishes nothing.  `NaN`, infinity, omitted later mesh rows, result-driven
search expansion, and partial canonical promotion are forbidden.  Formal mesh
execution remains unauthorized until the v6 result-blind post-result auditor,
its complete synthetic-PASS adversarial suite, the no-cycle protocol, and the
entire repaired package pass a fresh independent pre-run attack.

## 9. Claim boundary after a successful discovery

A successful result may say only that the same frozen finite-volume family
showed a low-mesh allocation-cusp discovery, two local fold branches, a remote
pair, and bounded one-/two-/three-retained-maximum representatives on two
same-family discovery meshes, 65 and 97.  Mesh 97 may be described only as a
low-mesh discovery confirmation, never as held out.  It may not claim held-out confirmation, mesh convergence, parity,
box robustness, an unbounded or continuum cusp, global exact modal counts,
independent-solver verification, or PRR readiness.

Before any mesh 113/128/129/161 or enlarged-box run, a separate truly held-out Stage-B
manifest must freeze the Stage-A result hash, representative physical weights,
branch orientations and comparison nodes, every confirmation row, and all
margin-aware error rules.  Stage B may re-solve the same equations but may not
refit physical controls.
