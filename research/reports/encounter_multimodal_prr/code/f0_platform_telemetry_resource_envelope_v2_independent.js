#!/usr/bin/env node
"use strict";

/*
 * Result-free independent verifier for the F0 v2 resource-envelope candidate.
 *
 * This implementation uses only the Node.js standard library.  It does not
 * import the Python verifier, execute a numerical worker, contact a network,
 * or grant any execution/science authority.
 */

const crypto = require("node:crypto");
const fs = require("node:fs");

const SCHEMA = "f0_platform_telemetry_resource_envelope_v2";
const COMPUTATIONAL_SCHEMA = "f0_computational_projection_v2";
const MEASUREMENT_SCHEMA = "f0_platform_measurement_v2";
const STATUS_CANDIDATE = "PASS_RESOURCE_ENVELOPE_CANDIDATE_NOT_F0";
const STATUS_HOLD = "HOLD_F0_RESOURCE_ENVELOPE_V2";

const MAXIMUM_RSS_BYTES = 32 * 1024 ** 3;
const MAXIMUM_WORKER_SECONDS = 4500;
const MAXIMUM_DARWIN_FOOTPRINT_BYTES = 24 * 1024 ** 3;
const MAXIMUM_SWAP_DELTA = 0;
const ZERO_SHA256 = "0".repeat(64);

const ROOT_KEYS = [
  "authority",
  "computational_projection",
  "computational_projection_sha256",
  "envelope",
  "failure_reasons",
  "legacy_source_schema",
  "legacy_source_status",
  "payload_binding_sha256",
  "platform_telemetry",
  "platform_telemetry_sha256",
  "post_job_accounting_required",
  "promotion_flags",
  "schema",
  "status",
];
const BINDING_KEYS = [
  "contract_sha256",
  "executable_sha256",
  "fixture_manifest_sha256",
  "runtime_sha256",
  "source_tree_sha256",
];
const MEASUREMENT_KEYS = [
  "architecture",
  "host_peak_footprint_bytes",
  "host_peak_footprint_method",
  "peak_rss_bytes",
  "platform",
  "process_swap_delta",
  "schema",
  "wall_seconds_hex",
  "worker_exit_code",
  "worker_signal",
];

const AUTHORITY = Object.freeze({
  certificate: false,
  execution: false,
  f0: false,
  f1: false,
  f2: false,
  f3: false,
  manuscript: false,
  network: false,
  remote: false,
  science: false,
  slurm: false,
  ssh: false,
});
const PROMOTION_FLAGS = Object.freeze({
  authorizes_f0: false,
  authorizes_f1: false,
  authorizes_f2: false,
  authorizes_f3: false,
  authorizes_manuscript: false,
  authorizes_remote: false,
  authorizes_science: false,
  independent_audit_complete: false,
  production_resource_gate: false,
  resource_candidate_only: true,
  science_executed: false,
});
const METHOD_COUNTS = Object.freeze({
  canonical_scalar_record_count: 27019,
  compiled_power_stream_run_count: 1,
  mandatory_tail_evaluation_count: 4,
  maximum_power_index: 27018,
  p_action_call_count: 27018,
  repeated_p_actions_during_reevaluation: 0,
  topology_evaluation_count: 512,
});

class VerificationError extends Error {
  constructor(message) {
    super(message);
    this.name = "VerificationError";
  }
}

class JsonNumber {
  constructor(raw) {
    this.raw = raw;
    this.value = Number(raw);
    Object.freeze(this);
  }
}

function fail(message) {
  throw new VerificationError(message);
}

function isObject(value) {
  return value !== null && typeof value === "object" &&
    !Array.isArray(value) && !(value instanceof JsonNumber);
}

function exactKeys(value, keys, label) {
  if (!isObject(value)) {
    fail(`${label} is not an object`);
  }
  const observed = Object.keys(value).sort();
  const expected = [...keys].sort();
  if (
    observed.length !== expected.length ||
    observed.some((key, index) => key !== expected[index])
  ) {
    fail(`${label} key set drifted`);
  }
}

function jsonString(value) {
  let result = '"';
  for (let index = 0; index < value.length; index += 1) {
    const code = value.charCodeAt(index);
    if (code === 0x22) result += '\\"';
    else if (code === 0x5c) result += "\\\\";
    else if (code === 0x08) result += "\\b";
    else if (code === 0x0c) result += "\\f";
    else if (code === 0x0a) result += "\\n";
    else if (code === 0x0d) result += "\\r";
    else if (code === 0x09) result += "\\t";
    else if (code < 0x20 || code > 0x7f) {
      result += `\\u${code.toString(16).padStart(4, "0")}`;
    } else {
      result += value[index];
    }
  }
  return `${result}"`;
}

function canonicalText(value) {
  if (value instanceof JsonNumber) return value.raw;
  if (value === null) return "null";
  if (value === true) return "true";
  if (value === false) return "false";
  if (typeof value === "string") return jsonString(value);
  if (Array.isArray(value)) {
    return `[${value.map(canonicalText).join(",")}]`;
  }
  if (isObject(value)) {
    return `{${Object.keys(value).sort().map(
      (key) => `${jsonString(key)}:${canonicalText(value[key])}`,
    ).join(",")}}`;
  }
  fail("unsupported canonical JSON value");
}

function canonicalBytes(value) {
  return Buffer.from(canonicalText(value), "ascii");
}

function sha256(payload) {
  return crypto.createHash("sha256").update(payload).digest("hex");
}

class StrictParser {
  constructor(payload) {
    if (!Buffer.isBuffer(payload) || payload.length === 0 ||
        payload.length > 16 * 1024 ** 2) {
      fail("canonical JSON byte shape is invalid");
    }
    for (const byte of payload) {
      if (byte > 0x7f) fail("canonical JSON is not ASCII");
    }
    this.text = payload.toString("ascii");
    this.index = 0;
  }

  parse() {
    const value = this.parseValue(0);
    if (this.index !== this.text.length) fail("trailing JSON bytes");
    if (!canonicalBytes(value).equals(Buffer.from(this.text, "ascii"))) {
      fail("JSON bytes are not canonical");
    }
    return value;
  }

  parseValue(depth) {
    if (depth > 128) fail("JSON nesting is excessive");
    const character = this.text[this.index];
    if (character === "{") return this.parseObject(depth + 1);
    if (character === "[") return this.parseArray(depth + 1);
    if (character === '"') return this.parseString();
    if (character === "t" && this.take("true")) return true;
    if (character === "f" && this.take("false")) return false;
    if (character === "n" && this.take("null")) return null;
    if (character === "-" || (character >= "0" && character <= "9")) {
      return this.parseNumber();
    }
    fail("canonical JSON parse failed");
  }

  take(token) {
    if (this.text.slice(this.index, this.index + token.length) !== token) {
      return false;
    }
    this.index += token.length;
    return true;
  }

  parseObject(depth) {
    this.index += 1;
    const result = Object.create(null);
    const observed = new Set();
    if (this.text[this.index] === "}") {
      this.index += 1;
      return result;
    }
    while (true) {
      if (this.text[this.index] !== '"') fail("object key is invalid");
      const key = this.parseString();
      if (observed.has(key)) fail("duplicate JSON key");
      observed.add(key);
      if (this.text[this.index] !== ":") fail("object colon is missing");
      this.index += 1;
      result[key] = this.parseValue(depth);
      const delimiter = this.text[this.index];
      if (delimiter === "}") {
        this.index += 1;
        return result;
      }
      if (delimiter !== ",") fail("object delimiter is invalid");
      this.index += 1;
    }
  }

  parseArray(depth) {
    this.index += 1;
    const result = [];
    if (this.text[this.index] === "]") {
      this.index += 1;
      return result;
    }
    while (true) {
      result.push(this.parseValue(depth));
      const delimiter = this.text[this.index];
      if (delimiter === "]") {
        this.index += 1;
        return result;
      }
      if (delimiter !== ",") fail("array delimiter is invalid");
      this.index += 1;
    }
  }

  parseString() {
    this.index += 1;
    let result = "";
    while (this.index < this.text.length) {
      const character = this.text[this.index];
      this.index += 1;
      if (character === '"') return result;
      if (character === "\\") {
        const escape = this.text[this.index];
        this.index += 1;
        const simple = {
          '"': '"',
          "\\": "\\",
          "/": "/",
          b: "\b",
          f: "\f",
          n: "\n",
          r: "\r",
          t: "\t",
        };
        if (Object.hasOwn(simple, escape)) {
          result += simple[escape];
        } else if (escape === "u") {
          const digits = this.text.slice(this.index, this.index + 4);
          if (!/^[0-9a-fA-F]{4}$/.test(digits)) fail("Unicode escape is invalid");
          result += String.fromCharCode(Number.parseInt(digits, 16));
          this.index += 4;
        } else {
          fail("string escape is invalid");
        }
      } else {
        if (character.charCodeAt(0) < 0x20) fail("string control byte is invalid");
        result += character;
      }
    }
    fail("unterminated string");
  }

  parseNumber() {
    const rest = this.text.slice(this.index);
    const match = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(rest);
    if (match === null) fail("number token is invalid");
    const raw = match[0];
    const value = Number(raw);
    if (!Number.isFinite(value)) fail("number is nonfinite");

    let expected;
    if (!raw.includes(".") && !/[eE]/.test(raw)) {
      expected = value.toString();
      if (raw === "-0") expected = "0";
    } else if (Number.isInteger(value)) {
      expected = `${value.toString()}.0`;
    } else {
      expected = value.toString();
    }
    if (raw !== expected) fail("number token is not Python-canonical");
    this.index += raw.length;
    return new JsonNumber(raw);
  }
}

function strictParse(payload) {
  return new StrictParser(payload).parse();
}

function requireString(value, label) {
  if (typeof value !== "string") fail(`${label} is not a string`);
  return value;
}

function requireSha(value, label) {
  if (typeof value !== "string" || !/^[0-9a-f]{64}$/.test(value)) {
    fail(`${label} is not lowercase SHA-256`);
  }
  return value;
}

function requireInteger(value, label, minimum = 0) {
  if (!(value instanceof JsonNumber) ||
      value.raw.includes(".") || /[eE]/.test(value.raw) ||
      !Number.isSafeInteger(value.value) || value.value < minimum) {
    fail(`${label} is not a bounded plain integer`);
  }
  return value.value;
}

function requireFloat(value, label) {
  if (!(value instanceof JsonNumber) || !value.raw.includes(".") ||
      !Number.isFinite(value.value)) {
    fail(`${label} is not a canonical float`);
  }
  return value.value;
}

function deepEqual(left, right) {
  return canonicalText(left) === canonicalText(right);
}

function asJson(value) {
  if (typeof value === "number") {
    if (!Number.isSafeInteger(value)) fail("unsafe internal integer");
    return new JsonNumber(value.toString());
  }
  if (Array.isArray(value)) return value.map(asJson);
  if (isObject(value)) {
    const result = Object.create(null);
    for (const [key, child] of Object.entries(value)) result[key] = asJson(child);
    return result;
  }
  return value;
}

function pythonFloatHex(value) {
  if (!Number.isFinite(value)) fail("wall seconds is nonfinite");
  if (Object.is(value, -0)) return "-0x0.0p+0";
  if (value === 0) return "0x0.0p+0";
  const buffer = new ArrayBuffer(8);
  const view = new DataView(buffer);
  view.setFloat64(0, value, false);
  const bits = view.getBigUint64(0, false);
  const negative = (bits >> 63n) !== 0n;
  const exponentBits = Number((bits >> 52n) & 0x7ffn);
  const fraction = bits & ((1n << 52n) - 1n);
  const prefix = negative ? "-" : "";
  const fractionHex = fraction.toString(16).padStart(13, "0");
  if (exponentBits === 0) return `${prefix}0x0.${fractionHex}p-1022`;
  const exponent = exponentBits - 1023;
  return `${prefix}0x1.${fractionHex}p${exponent >= 0 ? "+" : ""}${exponent}`;
}

function parsePythonFloatHex(text) {
  requireString(text, "wall_seconds_hex");
  if (text === "0x0.0p+0") return 0;
  const match = /^0x([01])\.([0-9a-f]{13})p([+-][0-9]+)$/.exec(text);
  if (match === null) fail("wall seconds hexadecimal text is invalid");
  const leading = Number(match[1]);
  const fraction = Number(BigInt(`0x${match[2]}`)) / 2 ** 52;
  const exponent = Number.parseInt(match[3], 10);
  const value = (leading + fraction) * 2 ** exponent;
  if (!Number.isFinite(value) || value < 0 || pythonFloatHex(value) !== text) {
    fail("wall seconds is noncanonical or unbounded");
  }
  return value;
}

function validateProjection(value) {
  exactKeys(value, [
    "bindings",
    "method_counts",
    "schedule_sha256",
    "schema",
    "shape",
    "state_count",
  ], "computational projection");
  if (value.schema !== COMPUTATIONAL_SCHEMA) fail("computational schema drifted");
  if (!Array.isArray(value.shape) || value.shape.length !== 3 ||
      [207, 215, 161].some(
        (expected, index) =>
          requireInteger(value.shape[index], `shape[${index}]`) !== expected,
      )) {
    fail("formal shape drifted");
  }
  if (requireInteger(value.state_count, "state_count") !== 7165305) {
    fail("formal state count drifted");
  }
  requireSha(value.schedule_sha256, "schedule_sha256");
  exactKeys(value.bindings, BINDING_KEYS, "computational bindings");
  for (const key of BINDING_KEYS) requireSha(value.bindings[key], key);
  exactKeys(value.method_counts, Object.keys(METHOD_COUNTS), "method counts");
  for (const [key, expected] of Object.entries(METHOD_COUNTS)) {
    if (requireInteger(value.method_counts[key], key) !== expected) {
      fail("formal method counts drifted");
    }
  }
}

function validateMeasurement(telemetry) {
  exactKeys(telemetry, [
    ...MEASUREMENT_KEYS,
    "darwin_footprint_bytes_upper_bound",
    "rss_bytes_upper_bound",
    "wall_seconds_upper_bound",
  ], "platform telemetry");
  if (telemetry.schema !== MEASUREMENT_SCHEMA) fail("measurement schema drifted");
  if (telemetry.platform !== "darwin" && telemetry.platform !== "linux") {
    fail("platform is unsupported");
  }
  if (typeof telemetry.architecture !== "string" ||
      !/^[a-z0-9_+-]{1,32}$/.test(telemetry.architecture)) {
    fail("architecture is noncanonical");
  }
  const wallSeconds = parsePythonFloatHex(telemetry.wall_seconds_hex);
  const peakRssBytes = requireInteger(telemetry.peak_rss_bytes, "peak_rss_bytes");
  const processSwapDelta = requireInteger(
    telemetry.process_swap_delta,
    "process_swap_delta",
  );
  const workerExitCode = requireInteger(
    telemetry.worker_exit_code,
    "worker_exit_code",
  );
  let workerSignal = null;
  if (telemetry.worker_signal !== null) {
    workerSignal = requireInteger(telemetry.worker_signal, "worker_signal", 1);
  }
  let hostPeakFootprintBytes = null;
  if (telemetry.host_peak_footprint_bytes !== null) {
    hostPeakFootprintBytes = requireInteger(
      telemetry.host_peak_footprint_bytes,
      "host_peak_footprint_bytes",
    );
  }
  if (typeof telemetry.host_peak_footprint_method !== "string" ||
      telemetry.host_peak_footprint_method.length === 0 ||
      telemetry.host_peak_footprint_method.length > 96) {
    fail("footprint method is invalid");
  }
  if (telemetry.platform === "darwin") {
    if (hostPeakFootprintBytes === null ||
        telemetry.host_peak_footprint_method !== "darwin_phys_footprint_peak") {
      fail("Darwin footprint relation drifted");
    }
  } else {
    const method = telemetry.host_peak_footprint_method;
    if (method !== "host_footprint_tool_unavailable" &&
        method !== "linux_cgroup_v2_memory_peak") {
      fail("Linux footprint method is invalid");
    }
    if ((method === "host_footprint_tool_unavailable" &&
         hostPeakFootprintBytes !== null) ||
        (method === "linux_cgroup_v2_memory_peak" &&
         hostPeakFootprintBytes === null)) {
      fail("Linux footprint value/method relation drifted");
    }
  }
  if (requireInteger(
    telemetry.rss_bytes_upper_bound,
    "rss_bytes_upper_bound",
  ) !== MAXIMUM_RSS_BYTES) {
    fail("platform telemetry RSS envelope drifted");
  }
  if (requireFloat(
    telemetry.wall_seconds_upper_bound,
    "wall_seconds_upper_bound",
  ) !== MAXIMUM_WORKER_SECONDS) {
    fail("platform telemetry wall envelope drifted");
  }
  if (telemetry.platform === "darwin") {
    if (requireInteger(
      telemetry.darwin_footprint_bytes_upper_bound,
      "darwin_footprint_bytes_upper_bound",
    ) !== MAXIMUM_DARWIN_FOOTPRINT_BYTES) {
      fail("platform telemetry Darwin envelope drifted");
    }
  } else if (telemetry.darwin_footprint_bytes_upper_bound !== null) {
    fail("platform telemetry Linux envelope drifted");
  }
  return {
    hostPeakFootprintBytes,
    peakRssBytes,
    processSwapDelta,
    wallSeconds,
    workerExitCode,
    workerSignal,
  };
}

function validateLegacyLabel(value, label) {
  if (value === null) return;
  if (typeof value !== "string" ||
      !/^[A-Za-z0-9_.+-]{1,128}$/.test(value)) {
    fail(`${label} is invalid`);
  }
}

function verifyCandidateBytes(payload, expectedProjectionSha256) {
  requireSha(expectedProjectionSha256, "expected computational projection SHA-256");
  const decoded = strictParse(payload);
  exactKeys(decoded, ROOT_KEYS, "candidate");
  if (decoded.schema !== SCHEMA) fail("candidate schema drifted");
  if (decoded.post_job_accounting_required !== true) {
    fail("post-job accounting requirement drifted");
  }
  if (!deepEqual(decoded.authority, asJson(AUTHORITY))) {
    fail("candidate authority drifted");
  }
  if (!deepEqual(decoded.promotion_flags, asJson(PROMOTION_FLAGS))) {
    fail("candidate promotion flags drifted");
  }

  validateProjection(decoded.computational_projection);
  const computedProjectionSha = sha256(
    canonicalBytes(decoded.computational_projection),
  );
  requireSha(
    decoded.computational_projection_sha256,
    "computational_projection_sha256",
  );
  if (decoded.computational_projection_sha256 !== computedProjectionSha) {
    fail("computational projection binding failed");
  }
  if (computedProjectionSha !== expectedProjectionSha256) {
    fail("external computational projection SHA-256 mismatch");
  }

  const expectedEnvelope = asJson({
    maximum_darwin_footprint_bytes: MAXIMUM_DARWIN_FOOTPRINT_BYTES,
    maximum_process_swap_delta: MAXIMUM_SWAP_DELTA,
    maximum_rss_bytes: MAXIMUM_RSS_BYTES,
    maximum_worker_seconds_hex: "0x1.1940000000000p+12",
    scheduler_memory_request_bytes: 64 * 1024 ** 3,
    scheduler_wall_request_seconds: 7200,
  });
  if (!deepEqual(decoded.envelope, expectedEnvelope)) {
    fail("candidate envelope drifted");
  }

  const measurement = validateMeasurement(decoded.platform_telemetry);
  requireSha(decoded.platform_telemetry_sha256, "platform_telemetry_sha256");
  if (decoded.platform_telemetry_sha256 !==
      sha256(canonicalBytes(decoded.platform_telemetry))) {
    fail("platform telemetry binding failed");
  }

  const observedPayloadBinding = requireSha(
    decoded.payload_binding_sha256,
    "payload_binding_sha256",
  );
  const provisional = Object.assign(Object.create(null), decoded);
  provisional.payload_binding_sha256 = ZERO_SHA256;
  if (observedPayloadBinding !== sha256(canonicalBytes(provisional))) {
    fail("candidate payload binding failed");
  }

  validateLegacyLabel(decoded.legacy_source_schema, "legacy_source_schema");
  validateLegacyLabel(decoded.legacy_source_status, "legacy_source_status");
  const failures = [];
  if (measurement.wallSeconds > MAXIMUM_WORKER_SECONDS) {
    failures.push("wall_cap_exceeded");
  }
  if (measurement.peakRssBytes > MAXIMUM_RSS_BYTES) {
    failures.push("rss_cap_exceeded");
  }
  if (measurement.processSwapDelta > MAXIMUM_SWAP_DELTA) {
    failures.push("process_swap_cap_exceeded");
  }
  if (measurement.workerExitCode !== 0) failures.push("worker_exit_nonzero");
  if (measurement.workerSignal !== null) failures.push("worker_signal_observed");
  if (decoded.platform_telemetry.platform === "darwin" &&
      measurement.hostPeakFootprintBytes > MAXIMUM_DARWIN_FOOTPRINT_BYTES) {
    failures.push("darwin_footprint_cap_exceeded");
  }
  if (decoded.legacy_source_schema !== null ||
      decoded.legacy_source_status !== null) {
    failures.push("legacy_v1_observation_not_reinterpretable");
  }
  const expectedFailures = [...new Set(failures)].sort();
  if (!Array.isArray(decoded.failure_reasons) ||
      decoded.failure_reasons.some((value) => typeof value !== "string") ||
      decoded.failure_reasons.length !== expectedFailures.length ||
      decoded.failure_reasons.some(
        (value, index) => value !== expectedFailures[index],
      )) {
    fail("candidate findings were not independently recomputed");
  }
  const expectedStatus = expectedFailures.length === 0
    ? STATUS_CANDIDATE
    : STATUS_HOLD;
  if (decoded.status !== expectedStatus) {
    fail("candidate status/finding relation drifted");
  }
  return Object.freeze({
    computationalProjectionSha256: computedProjectionSha,
    failureReasons: Object.freeze(expectedFailures),
    payloadBindingSha256: observedPayloadBinding,
    status: expectedStatus,
    zeroAuthority: true,
  });
}

function usage() {
  return [
    "usage:",
    "  node f0_platform_telemetry_resource_envelope_v2_independent.js",
    "    --candidate PATH",
    "    --expected-computational-projection-sha256 SHA256",
  ].join(" ");
}

function main(argv) {
  let candidatePath = null;
  let expectedProjectionSha256 = null;
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--candidate" && index + 1 < argv.length) {
      candidatePath = argv[++index];
    } else if (
      argument === "--expected-computational-projection-sha256" &&
      index + 1 < argv.length
    ) {
      expectedProjectionSha256 = argv[++index];
    } else {
      fail(usage());
    }
  }
  if (candidatePath === null || expectedProjectionSha256 === null) fail(usage());
  const result = verifyCandidateBytes(
    fs.readFileSync(candidatePath),
    expectedProjectionSha256,
  );
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

if (require.main === module) {
  try {
    main(process.argv.slice(2));
  } catch (error) {
    const message = error instanceof Error ? error.message : "verification failed";
    process.stderr.write(`HOLD: ${message}\n`);
    process.exitCode = 1;
  }
}

module.exports = Object.freeze({
  VerificationError,
  canonicalBytes,
  sha256,
  strictParse,
  verifyCandidateBytes,
});
