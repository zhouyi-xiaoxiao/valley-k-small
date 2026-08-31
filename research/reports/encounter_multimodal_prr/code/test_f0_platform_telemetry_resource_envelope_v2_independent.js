#!/usr/bin/env node
"use strict";

const assert = require("node:assert/strict");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const test = require("node:test");

const verifier = require("./f0_platform_telemetry_resource_envelope_v2_independent.js");

const CODE_ROOT = __dirname;
const PYTHON_GENERATOR = String.raw`
import json
import math
import sys
import f0_platform_telemetry_resource_envelope_v2 as r

mode = sys.argv[1]
projection = {
    "bindings": {
        "contract_sha256": "1" * 64,
        "executable_sha256": "2" * 64,
        "fixture_manifest_sha256": "3" * 64,
        "runtime_sha256": "4" * 64,
        "source_tree_sha256": "5" * 64,
    },
    "method_counts": {
        "canonical_scalar_record_count": 27019,
        "compiled_power_stream_run_count": 1,
        "mandatory_tail_evaluation_count": 4,
        "maximum_power_index": 27018,
        "p_action_call_count": 27018,
        "repeated_p_actions_during_reevaluation": 0,
        "topology_evaluation_count": 512,
    },
    "schedule_sha256": "6" * 64,
    "schema": r.COMPUTATIONAL_SCHEMA,
    "shape": [207, 215, 161],
    "state_count": 7165305,
}
wall = r.MAXIMUM_WORKER_SECONDS
rss = r.MAXIMUM_RSS_BYTES
footprint = r.MAXIMUM_DARWIN_FOOTPRINT_BYTES
legacy = {}
if mode == "rss_plus_one":
    rss += 1
elif mode == "wall_plus_one_ulp":
    wall = math.nextafter(wall, math.inf)
elif mode == "legacy":
    legacy = {
        "legacy_source_schema": "f0_resource_observation_v1",
        "legacy_source_status": "HOLD_F0_METHOD_OR_RESOURCE",
    }
measurement = r.PlatformMeasurement(
    schema=r.MEASUREMENT_SCHEMA,
    platform="darwin",
    architecture="arm64",
    wall_seconds_hex=wall.hex(),
    peak_rss_bytes=rss,
    process_swap_delta=0,
    worker_exit_code=0,
    worker_signal=None,
    host_peak_footprint_bytes=footprint,
    host_peak_footprint_method="darwin_phys_footprint_peak",
)
candidate = r.build_resource_envelope_candidate(
    projection,
    measurement,
    **legacy,
)
sys.stdout.buffer.write(r.canonical_json_bytes(candidate))
`;

function pythonCandidate(mode = "clean") {
  const generated = spawnSync(
    "python3",
    ["-B", "-c", PYTHON_GENERATOR, mode],
    {
      cwd: CODE_ROOT,
      encoding: null,
      env: {
        ...process.env,
        PYTHONDONTWRITEBYTECODE: "1",
      },
    },
  );
  assert.equal(generated.status, 0, generated.stderr.toString());
  assert.equal(generated.stderr.length, 0);
  return generated.stdout;
}

function decodedCandidate(mode = "clean") {
  return verifier.strictParse(pythonCandidate(mode));
}

function expectedProjectionSha(candidate) {
  return verifier.sha256(
    verifier.canonicalBytes(candidate.computational_projection),
  );
}

function rebound(candidate) {
  candidate.payload_binding_sha256 = "0".repeat(64);
  candidate.payload_binding_sha256 = verifier.sha256(
    verifier.canonicalBytes(candidate),
  );
  return verifier.canonicalBytes(candidate);
}

function reboundTelemetry(candidate) {
  candidate.platform_telemetry_sha256 = verifier.sha256(
    verifier.canonicalBytes(candidate.platform_telemetry),
  );
  return rebound(candidate);
}

test("accepts a Python-generated exact-boundary nonauthorizing candidate", () => {
  const payload = pythonCandidate();
  const candidate = verifier.strictParse(payload);
  const result = verifier.verifyCandidateBytes(
    payload,
    expectedProjectionSha(candidate),
  );
  assert.equal(result.status, "PASS_RESOURCE_ENVELOPE_CANDIDATE_NOT_F0");
  assert.deepEqual(result.failureReasons, []);
  assert.equal(result.zeroAuthority, true);
});

test("accepts independently recomputed one-unit and one-ULP boundary HOLDs", () => {
  for (const [mode, reason] of [
    ["rss_plus_one", "rss_cap_exceeded"],
    ["wall_plus_one_ulp", "wall_cap_exceeded"],
  ]) {
    const payload = pythonCandidate(mode);
    const candidate = verifier.strictParse(payload);
    const result = verifier.verifyCandidateBytes(
      payload,
      expectedProjectionSha(candidate),
    );
    assert.equal(result.status, "HOLD_F0_RESOURCE_ENVELOPE_V2");
    assert.deepEqual(result.failureReasons, [reason]);
  }
});

test("accepts legacy only as an explicit nonpromotable HOLD", () => {
  const payload = pythonCandidate("legacy");
  const candidate = verifier.strictParse(payload);
  const result = verifier.verifyCandidateBytes(
    payload,
    expectedProjectionSha(candidate),
  );
  assert.equal(result.status, "HOLD_F0_RESOURCE_ENVELOPE_V2");
  assert.deepEqual(
    result.failureReasons,
    ["legacy_v1_observation_not_reinterpretable"],
  );
});

test("rejects fully rebound telemetry/findings and legacy promotion tampering", () => {
  {
    const candidate = decodedCandidate();
    const expected = expectedProjectionSha(candidate);
    candidate.platform_telemetry.peak_rss_bytes =
      verifier.strictParse(Buffer.from("34359738369"));
    assert.throws(
      () => verifier.verifyCandidateBytes(reboundTelemetry(candidate), expected),
      /findings were not independently recomputed/,
    );
  }
  {
    const candidate = decodedCandidate("legacy");
    const expected = expectedProjectionSha(candidate);
    candidate.failure_reasons = [];
    candidate.status = "PASS_RESOURCE_ENVELOPE_CANDIDATE_NOT_F0";
    assert.throws(
      () => verifier.verifyCandidateBytes(rebound(candidate), expected),
      /findings were not independently recomputed/,
    );
  }
});

test("external projection digest rejects a fully internally rebound projection", () => {
  const candidate = decodedCandidate();
  const externallyExpected = expectedProjectionSha(candidate);
  candidate.computational_projection.bindings.runtime_sha256 = "9".repeat(64);
  candidate.computational_projection_sha256 = verifier.sha256(
    verifier.canonicalBytes(candidate.computational_projection),
  );
  assert.throws(
    () => verifier.verifyCandidateBytes(rebound(candidate), externallyExpected),
    /external computational projection SHA-256 mismatch/,
  );
});

test("zero authority and promotion flags cannot be rebound to true", () => {
  const candidate = decodedCandidate();
  const expected = expectedProjectionSha(candidate);
  candidate.authority.remote = true;
  assert.throws(
    () => verifier.verifyCandidateBytes(rebound(candidate), expected),
    /candidate authority drifted/,
  );
});

test("strict parser rejects duplicate, malformed, and noncanonical JSON", () => {
  const malformed = [
    Buffer.from('{"schema":"a","schema":"b"}'),
    Buffer.from('{"value":1e0}'),
    Buffer.from('{"value":01}'),
    Buffer.from('{"value":"\\/" }'),
    Buffer.from('{"value":NaN}'),
    Buffer.from('{"value":1}\n'),
    Buffer.from('{"z":0,"a":0}'),
    Buffer.from('{"value":"\xc3\xa9"}', "binary"),
  ];
  for (const payload of malformed) {
    assert.throws(() => verifier.strictParse(payload), verifier.VerificationError);
  }
});

test("CLI requires and verifies the external projection digest", () => {
  const payload = pythonCandidate();
  const candidate = verifier.strictParse(payload);
  const expected = expectedProjectionSha(candidate);
  const temporary = path.join(
    process.env.TMPDIR || "/tmp",
    `f0-v2-independent-${process.pid}.json`,
  );
  require("node:fs").writeFileSync(temporary, payload, { flag: "wx", mode: 0o600 });
  try {
    const result = spawnSync(
      process.execPath,
      [
        path.join(
          CODE_ROOT,
          "f0_platform_telemetry_resource_envelope_v2_independent.js",
        ),
        "--candidate",
        temporary,
        "--expected-computational-projection-sha256",
        expected,
      ],
      { encoding: "utf8" },
    );
    assert.equal(result.status, 0, result.stderr);
    const summary = JSON.parse(result.stdout);
    assert.equal(summary.computationalProjectionSha256, expected);
    assert.equal(summary.zeroAuthority, true);
  } finally {
    require("node:fs").unlinkSync(temporary);
  }
});
