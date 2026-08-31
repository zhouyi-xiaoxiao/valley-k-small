from __future__ import annotations

import copy
import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Callable

import build_continuum_c1_n0_runtime_authority_v1 as builder
import pytest
import validate_continuum_c1_n0_runtime_authority_v1 as validator

REPORT = Path(__file__).resolve().parent.parent
OPERATION_MODEL_BYTES = (REPORT / builder.OPERATION_MODEL_PATH).read_bytes()

REAL_SOURCE_PATHS = {
    builder.PYTHON_PATH: Path(
        "/opt/homebrew/Cellar/python@3.12/3.12.13/Frameworks/"
        "Python.framework/Versions/3.12/bin/python3.12"
    ),
    builder.GMPY2_WRAPPER_PATH: Path(".venv/lib/python3.12/site-packages/gmpy2/__init__.py"),
    builder.GMPY2_EXTENSION_PATH: Path(
        ".venv/lib/python3.12/site-packages/gmpy2/gmpy2.cpython-312-darwin.so"
    ),
    builder.GMP_PATH: Path(".venv/lib/python3.12/site-packages/gmpy2.libs/libgmp.10.dylib"),
    builder.MPFR_PATH: Path(".venv/lib/python3.12/site-packages/gmpy2.libs/libmpfr.6.dylib"),
    builder.MPC_PATH: Path(".venv/lib/python3.12/site-packages/gmpy2.libs/libmpc.3.dylib"),
}
REAL_RUNTIME_BYTES = {
    destination: source.read_bytes() for destination, source in REAL_SOURCE_PATHS.items()
}
LITERAL_EXPECTED_SHA256 = {
    builder.PYTHON_PATH: ("31b9c9a8d50289f3a13f014b3efd8ea3534fc3eea7ca7d9809e166139910b805"),
    builder.GMPY2_WRAPPER_PATH: (
        "3d4f21a0e9d6d32c935e3d39ef4be23a9a7d0ea56344ebbb0b8dca4f5651e8a2"
    ),
    builder.GMPY2_EXTENSION_PATH: (
        "9586b7c4b887704b57576f52b73a8c45437946d2b172095d82c20fa0871a415b"
    ),
    builder.GMP_PATH: ("22cec4689e503d590cfbf3373ae7f442ef6d40c3e6c93a3612bbd1b7e2bce049"),
    builder.MPFR_PATH: ("d314a427a901f8ece38b67966cd2fbf5642ceb7d1c2e5136f8282ca7ab859aed"),
    builder.MPC_PATH: ("d3c10c39234c095f5c1938ad607c87a0633152f51271d9ed1c494724430c2b0c"),
}
LITERAL_AUTHORITY_ROOT = (
    "/Users/ae23069/.local-build/valley-k-small/runtime-authorities/"
    "encounter-c1-n0-cpython-3.12.13-gmpy2-2.2.1-arm64-v1"
)
LITERAL_EXPECTATIONS = {
    "darwin_release": "25.5.0",
    "future_observation_requirement": (
        "FUTURE_AUTHENTICATED_RUNTIME_PROBE_REQUIRED_BEFORE_RUNTIME_CLOSURE"
    ),
    "gmp_version": "GMP 6.3.0",
    "gmpy2_version": "2.2.1",
    "machine": "arm64",
    "macos_build": "25F84",
    "mpc_version": "MPC 1.3.1",
    "mpfr_version": "MPFR 4.2.1",
    "python_full_version": (
        "3.12.13 (main, Mar  3 2026, 12:39:30) [Clang 17.0.0 (clang-1700.6.3.2)]"
    ),
    "python_soabi": "cpython-312-darwin",
    "status": "DECLARED_EXPECTATIONS_NOT_OBSERVED_BY_THIS_STATIC_INVENTORY",
}


def _files() -> dict[str, bytes]:
    return {
        builder.OPERATION_MODEL_PATH: OPERATION_MODEL_BYTES,
        **REAL_RUNTIME_BYTES,
    }


def _inventory() -> tuple[bytes, dict[str, bytes]]:
    files = _files()
    return builder.build_runtime_authority(files), files


def _canonical(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")


def _command_offsets(raw: bytes) -> list[int]:
    assert raw[:4] == b"\xcf\xfa\xed\xfe"
    ncmds, sizeofcmds = struct.unpack_from("<II", raw, 16)
    cursor = 32
    offsets: list[int] = []
    for _ in range(ncmds):
        offsets.append(cursor)
        _, size = struct.unpack_from("<II", raw, cursor)
        cursor += size
    assert cursor == 32 + sizeofcmds
    return offsets


def _patch_u32(raw: bytes, offset: int, value: int) -> bytes:
    mutated = bytearray(raw)
    struct.pack_into("<I", mutated, offset, value)
    return bytes(mutated)


def _fat_wrap(
    arm64: bytes,
    *,
    fat64: bool,
    table_subtype: int = 0,
    reserved: int = 0,
) -> bytes:
    x86 = struct.pack(
        "<IiiIIIII",
        0xFEEDFACF,
        0x01000007,
        3,
        builder.MH_EXECUTE,
        0,
        0,
        0,
        0,
    )
    width = 32 if fat64 else 20
    table_end = 8 + 2 * width
    x86_offset = (table_end + 7) // 8 * 8
    arm_offset = (x86_offset + len(x86) + 7) // 8 * 8
    result = bytearray(arm_offset + len(arm64))
    struct.pack_into(">II", result, 0, 0xCAFEBABF if fat64 else 0xCAFEBABE, 2)
    if fat64:
        struct.pack_into(
            ">iiQQII",
            result,
            8,
            0x01000007,
            3,
            x86_offset,
            len(x86),
            3,
            reserved,
        )
        struct.pack_into(
            ">iiQQII",
            result,
            40,
            builder.CPU_TYPE_ARM64,
            table_subtype,
            arm_offset,
            len(arm64),
            3,
            0,
        )
    else:
        struct.pack_into(
            ">iiIII",
            result,
            8,
            0x01000007,
            3,
            x86_offset,
            len(x86),
            3,
        )
        struct.pack_into(
            ">iiIII",
            result,
            28,
            builder.CPU_TYPE_ARM64,
            table_subtype,
            arm_offset,
            len(arm64),
            3,
        )
    result[x86_offset : x86_offset + len(x86)] = x86
    result[arm_offset : arm_offset + len(arm64)] = arm64
    return bytes(result)


def _assert_public_rejects(path: str, mutated_bytes: bytes) -> None:
    baseline, files = _inventory()
    files[path] = mutated_bytes
    with pytest.raises(builder.RuntimeAuthorityBuildFailure):
        builder.build_runtime_authority(files)
    with pytest.raises(validator.RuntimeAuthorityValidationFailure):
        validator.validate_runtime_authority(baseline, files)


def _assert_both_parsers_reject(image_id: str, raw: bytes) -> None:
    with pytest.raises(builder.RuntimeAuthorityBuildFailure):
        builder._parse_macho(raw, image_id)
    with pytest.raises(validator.RuntimeAuthorityValidationFailure):
        validator._parse_macho(raw, image_id)


def _assert_both_classifiers_reject(
    image_id: str,
    edges: list[dict[str, Any]],
) -> None:
    with pytest.raises(builder.RuntimeAuthorityBuildFailure):
        builder._classify_edges(image_id, copy.deepcopy(edges))
    with pytest.raises(validator.RuntimeAuthorityValidationFailure):
        validator._classify(image_id, copy.deepcopy(edges))


def test_live_bytes_build_and_validate_only_an_in_memory_static_inventory() -> None:
    raw, files = _inventory()
    document = validator.validate_runtime_authority(raw, files)
    assert document["schema"] == ("encounter_continuum_c1_n0_runtime_byte_pin_inventory_v1")
    assert "NO_PROBE_NO_RUNTIME_CLOSURE" in document["status"]
    assert document["authority_root"] == LITERAL_AUTHORITY_ROOT
    assert len(document["macho_images"]) == 5
    assert sum(len(image["edges"]) for image in document["macho_images"]) == 13


def test_exact_nonclaims_cover_root_path_metadata_import_and_runtime_closure() -> None:
    raw, files = _inventory()
    claim = validator.validate_runtime_authority(raw, files)["claim_boundary"]
    assert claim == {
        "authority_root_materialized": False,
        "candidate_execution_performed": False,
        "complete_runtime_closure_claimed": False,
        "host_runtime_bytes_complete": False,
        "import_resolution_observed": False,
        "operation_model_runtime_closure_substitution_allowed": False,
        "path_identity_observed": False,
        "pathname_toctou_closure_claimed": False,
        "runtime_probe_performed": False,
        "runtime_metadata_observed": False,
        "scientific_claim_made": False,
        "trust_boundary": (
            "CALLER_AUTHENTICATED_IMMUTABLE_BYTES_ONLY_NO_PATHNAME_OR_CONCURRENT_WRITER_CLAIM"
        ),
    }


def test_runtime_labels_are_exact_declared_unobserved_expectations() -> None:
    raw, files = _inventory()
    document = validator.validate_runtime_authority(raw, files)
    assert document["declared_unobserved_runtime_expectations"] == LITERAL_EXPECTATIONS
    assert "platform" not in document
    assert set(document["python"]) == {"path", "sha256"}
    assert "version" not in document["gmpy2"]
    assert all("version" not in item for item in document["numerical_libraries"])


def test_root_layout_and_byte_hash_oracles_are_literal_and_equal() -> None:
    assert builder.AUTHORITY_ROOT == validator.AUTHORITY_ROOT == LITERAL_AUTHORITY_ROOT
    literal_layout = {
        "python_executable": LITERAL_AUTHORITY_ROOT + "/bin/python3.12",
        "gmpy2_wrapper": (LITERAL_AUTHORITY_ROOT + "/site-packages/gmpy2/__init__.py"),
        "gmpy2_extension": (
            LITERAL_AUTHORITY_ROOT + "/site-packages/gmpy2/gmpy2.cpython-312-darwin.so"
        ),
        "gmp": (LITERAL_AUTHORITY_ROOT + "/site-packages/gmpy2.libs/libgmp.10.dylib"),
        "mpfr": (LITERAL_AUTHORITY_ROOT + "/site-packages/gmpy2.libs/libmpfr.6.dylib"),
        "mpc": (LITERAL_AUTHORITY_ROOT + "/site-packages/gmpy2.libs/libmpc.3.dylib"),
    }
    assert {
        "python_executable": builder.PYTHON_PATH,
        "gmpy2_wrapper": builder.GMPY2_WRAPPER_PATH,
        "gmpy2_extension": builder.GMPY2_EXTENSION_PATH,
        "gmp": builder.GMP_PATH,
        "mpfr": builder.MPFR_PATH,
        "mpc": builder.MPC_PATH,
    } == literal_layout
    assert {
        "python_executable": validator.PYTHON_PATH,
        "gmpy2_wrapper": validator.GMPY2_WRAPPER_PATH,
        "gmpy2_extension": validator.GMPY2_EXTENSION_PATH,
        "gmp": validator.GMP_PATH,
        "mpfr": validator.MPFR_PATH,
        "mpc": validator.MPC_PATH,
    } == literal_layout
    assert builder.EXPECTED_FILE_SHA256 == LITERAL_EXPECTED_SHA256
    assert validator.EXPECTED_FILE_SHA256 == LITERAL_EXPECTED_SHA256
    assert builder.EXPECTED_FILE_SHA256 is not validator.EXPECTED_FILE_SHA256
    assert set(REAL_RUNTIME_BYTES) == set(LITERAL_EXPECTED_SHA256)
    assert {
        path: hashlib.sha256(raw).hexdigest() for path, raw in REAL_RUNTIME_BYTES.items()
    } == LITERAL_EXPECTED_SHA256
    assert builder.GMPY2_EXTENSION_PATH == (
        LITERAL_AUTHORITY_ROOT + "/site-packages/gmpy2/gmpy2.cpython-312-darwin.so"
    )


def test_host_boundaries_are_exact_external_literal_edges() -> None:
    raw, files = _inventory()
    boundaries = validator.validate_runtime_authority(raw, files)["host_boundary_edges"]
    assert boundaries == [
        {
            "boundary_kind": "python_runtime",
            "path": (
                "/opt/homebrew/Cellar/python@3.12/3.12.13/Frameworks/"
                "Python.framework/Versions/3.12/Python"
            ),
        },
        {"boundary_kind": "apple_system", "path": "/usr/lib/dyld"},
        {"boundary_kind": "apple_system", "path": "/usr/lib/libSystem.B.dylib"},
    ]
    assert all(not item["path"].startswith(LITERAL_AUTHORITY_ROOT + "/") for item in boundaries)


def test_operation_model_runtime_substitution_is_explicitly_forbidden() -> None:
    raw, files = _inventory()
    document = validator.validate_runtime_authority(raw, files)
    assert document["operation_model"] == {
        "path": builder.OPERATION_MODEL_PATH,
        "process_contract_section_sha256": (
            "47ae856b647fa7be1119f68f684e36e253730bf2a87345ff634979d2893d4833"
        ),
        "schema": ("encounter_continuum_c1_n0_role10_numerical_operation_model_v2_candidate"),
        "sha256": ("ac0c2b185be75f0ecef3e331fdfd47fc674ca151fa6b26600aff9f789a2f8a6b"),
    }
    assert (
        document["claim_boundary"]["operation_model_runtime_closure_substitution_allowed"] is False
    )


def test_actual_macho_headers_and_command_sequences_match_literal_baseline() -> None:
    for image_id, path in builder.IMAGE_PATHS.items():
        built = builder._parse_macho(REAL_RUNTIME_BYTES[path], image_id)
        checked = validator._parse_macho(REAL_RUNTIME_BYTES[path], image_id)
        assert built == checked
        assert built["slice"]["endianness"] == "little"
        assert built["slice"]["cpusubtype"] == 0
        assert tuple(built["load_command_ids"]) == (builder.EXPECTED_COMMAND_SEQUENCES[image_id])


def test_lc_id_dylib_is_not_a_dependency_edge() -> None:
    for image_id in ("gmp", "mpc", "mpfr"):
        parsed = builder._parse_macho(REAL_RUNTIME_BYTES[builder.IMAGE_PATHS[image_id]], image_id)
        assert parsed["dylib_id"]["command_index"] == 4
        assert all(edge["command"] != "LC_ID_DYLIB" for edge in parsed["edges"])


@pytest.mark.parametrize("fat64", [False, True])
def test_separate_parsers_accept_structurally_valid_fat_arm64_selection(
    fat64: bool,
) -> None:
    raw = _fat_wrap(REAL_RUNTIME_BYTES[builder.GMPY2_EXTENSION_PATH], fat64=fat64)
    built = builder._parse_macho(raw, "gmpy2_extension")
    checked = validator._parse_macho(raw, "gmpy2_extension")
    assert built == checked
    assert built["slice"]["container"] == ("fat64" if fat64 else "fat32")
    _assert_public_rejects(builder.GMPY2_EXTENSION_PATH, raw)


@pytest.mark.parametrize("path", list(LITERAL_EXPECTED_SHA256))
def test_every_runtime_byte_substitution_hits_builder_and_validator(path: str) -> None:
    _assert_public_rejects(path, REAL_RUNTIME_BYTES[path] + b"X")


def test_operation_model_byte_substitution_hits_builder_and_validator() -> None:
    _assert_public_rejects(
        builder.OPERATION_MODEL_PATH,
        OPERATION_MODEL_BYTES.replace(b'"schema":', b'"schema" :', 1),
    )


class DictSubclass(dict[str, bytes]):
    pass


@pytest.mark.parametrize("kind", ["subclass", "missing", "extra", "mutable_value"])
def test_snapshot_requires_one_plain_exact_immutable_dict(kind: str) -> None:
    raw, files = _inventory()
    supplied: object
    if kind == "subclass":
        supplied = DictSubclass(files)
    else:
        changed: dict[str, Any] = dict(files)
        if kind == "missing":
            changed.pop(builder.GMPY2_WRAPPER_PATH)
        elif kind == "extra":
            changed[LITERAL_AUTHORITY_ROOT + "/extra"] = b"x"
        else:
            changed[builder.GMPY2_WRAPPER_PATH] = bytearray(changed[builder.GMPY2_WRAPPER_PATH])
        supplied = changed
    with pytest.raises(builder.RuntimeAuthorityBuildFailure):
        builder.build_runtime_authority(supplied)
    with pytest.raises(validator.RuntimeAuthorityValidationFailure):
        validator.validate_runtime_authority(raw, supplied)


def test_components_do_not_reopen_or_materialize_serialized_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    files = _files()

    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("filesystem path access forbidden")

    monkeypatch.setattr(Path, "open", forbidden)
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    monkeypatch.setattr(Path, "write_bytes", forbidden)
    monkeypatch.setattr(Path, "mkdir", forbidden)
    monkeypatch.setattr(Path, "resolve", forbidden)
    raw = builder.build_runtime_authority(files)
    validator.validate_runtime_authority(raw, files)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.__setitem__("schema", "runtime-authority-v1"),
        lambda d: d.__setitem__("status", "PASS"),
        lambda d: d.__setitem__("authority_root", "/caller/chosen/root"),
        lambda d: d.__setitem__("extra", {"result_sha256": "0" * 64}),
        lambda d: d["claim_boundary"].__setitem__("authority_root_materialized", True),
        lambda d: d["claim_boundary"].__setitem__("path_identity_observed", True),
        lambda d: d["claim_boundary"].__setitem__("complete_runtime_closure_claimed", True),
        lambda d: d["claim_boundary"].__setitem__("host_runtime_bytes_complete", True),
        lambda d: d["claim_boundary"].__setitem__("import_resolution_observed", True),
        lambda d: d["claim_boundary"].__setitem__("runtime_metadata_observed", True),
        lambda d: d["claim_boundary"].__setitem__(
            "operation_model_runtime_closure_substitution_allowed", True
        ),
        lambda d: d["declared_unobserved_runtime_expectations"].__setitem__(
            "python_full_version", "3.12.13 forged"
        ),
        lambda d: d["declared_unobserved_runtime_expectations"].__setitem__("machine", "x86_64"),
        lambda d: d["python"].__setitem__("path", "/caller/python"),
        lambda d: d["python"].__setitem__("full_version", "observed"),
        lambda d: d["gmpy2"]["wrapper"].__setitem__("path", "/caller/gmpy2.py"),
        lambda d: d["gmpy2"]["extension"].__setitem__("sha256", "0" * 64),
        lambda d: d["numerical_libraries"][0].__setitem__("version", "forged"),
        lambda d: d["host_boundary_edges"].reverse(),
        lambda d: d["host_boundary_edges"].append(
            {
                "boundary_kind": "apple_system",
                "path": LITERAL_AUTHORITY_ROOT + "/libPrivate.dylib",
            }
        ),
        lambda d: d["operation_model"].__setitem__("sha256", "0" * 64),
        lambda d: d["macho_images"].reverse(),
        lambda d: d["macho_images"][0]["load_command_ids"].reverse(),
        lambda d: d["macho_images"][0]["slice"].__setitem__("cpusubtype", 1),
        lambda d: d["macho_images"][1]["edges"][0].__setitem__("target_image_id", "gmp"),
    ],
)
def test_serialized_root_path_metadata_and_inventory_mutations_fail(
    mutate: Callable[[dict[str, Any]], Any],
) -> None:
    raw, files = _inventory()
    document = json.loads(raw)
    mutate(document)
    with pytest.raises(validator.RuntimeAuthorityValidationFailure):
        validator.validate_runtime_authority(_canonical(document), files)


def test_duplicate_json_key_fails_before_normalization() -> None:
    raw, files = _inventory()
    duplicate = raw.replace(
        b'{\n  "authority_root"',
        b'{\n  "schema": "duplicate",\n  "authority_root"',
        1,
    )
    with pytest.raises(
        validator.RuntimeAuthorityValidationFailure,
        match="duplicate JSON key",
    ):
        validator.validate_runtime_authority(duplicate, files)


@pytest.mark.parametrize(
    "invalid",
    [
        b'{"x":' + b"[" * 70 + b"0" + b"]" * 70 + b"}",
        b'{"x":"' + b"A" * (validator.MAX_TEXT_CHARS + 1) + b'"}',
        b" " * (validator.MAX_AUTHORITY_BYTES + 1),
        b'{"x":18446744073709551616}',
        b'{"x":1.0}',
        b'{"x":NaN}',
        b'{"x":"\\u00e9"}',
    ],
)
def test_json_depth_string_file_integer_and_type_caps_fail(invalid: bytes) -> None:
    _, files = _inventory()
    with pytest.raises(validator.RuntimeAuthorityValidationFailure):
        validator.validate_runtime_authority(invalid, files)


@pytest.mark.parametrize(
    "transform",
    [
        lambda raw: raw.rstrip(b"\n"),
        lambda raw: raw.replace(b"  ", b" ", 1),
        lambda raw: b"\xef\xbb\xbf" + raw,
    ],
)
def test_noncanonical_json_fails(transform: Callable[[bytes], bytes]) -> None:
    raw, files = _inventory()
    with pytest.raises(validator.RuntimeAuthorityValidationFailure):
        validator.validate_runtime_authority(transform(raw), files)


@pytest.mark.parametrize(
    "image_id",
    ["python_executable", "gmpy2_extension", "gmp", "mpfr", "mpc"],
)
def test_big_endian_images_hit_both_parsers_and_public_components(
    image_id: str,
) -> None:
    path = builder.IMAGE_PATHS[image_id]
    raw = bytearray(REAL_RUNTIME_BYTES[path])
    raw[:4] = b"\xfe\xed\xfa\xcf"
    mutated = bytes(raw)
    _assert_both_parsers_reject(image_id, mutated)
    _assert_public_rejects(path, mutated)


@pytest.mark.parametrize(
    ("name", "offset", "value"),
    [
        ("nonzero_header_reserved", 28, 1),
        ("nonzero_subtype", 8, 1),
        ("huge_ncmds", 16, 0xFFFFFFFF),
        ("huge_sizeofcmds", 20, 0xFFFFFFFF),
    ],
)
def test_header_mutations_hit_both_parsers_and_public_components(
    name: str,
    offset: int,
    value: int,
) -> None:
    del name
    path = builder.GMPY2_EXTENSION_PATH
    mutated = _patch_u32(REAL_RUNTIME_BYTES[path], offset, value)
    _assert_both_parsers_reject("gmpy2_extension", mutated)
    _assert_public_rejects(path, mutated)


@pytest.mark.parametrize("unknown", [0x7F, 0x8000007F])
def test_unknown_and_unknown_required_commands_hit_both_parsers(
    unknown: int,
) -> None:
    path = builder.GMPY2_EXTENSION_PATH
    offsets = _command_offsets(REAL_RUNTIME_BYTES[path])
    mutated = _patch_u32(REAL_RUNTIME_BYTES[path], offsets[0], unknown)
    _assert_both_parsers_reject("gmpy2_extension", mutated)
    _assert_public_rejects(path, mutated)


@pytest.mark.parametrize(
    "forbidden",
    [
        builder.LC_LOAD_WEAK_DYLIB,
        builder.LC_REEXPORT_DYLIB,
        builder.LC_LAZY_LOAD_DYLIB,
        builder.LC_LOAD_UPWARD_DYLIB,
        builder.LC_RPATH,
        builder.LC_DYLD_ENVIRONMENT,
    ],
)
def test_weak_reexport_lazy_upward_rpath_and_environment_commands_fail(
    forbidden: int,
) -> None:
    path = builder.GMPY2_EXTENSION_PATH
    offsets = _command_offsets(REAL_RUNTIME_BYTES[path])
    mutated = _patch_u32(REAL_RUNTIME_BYTES[path], offsets[10], forbidden)
    _assert_both_parsers_reject("gmpy2_extension", mutated)
    _assert_public_rejects(path, mutated)


def test_known_nonedge_in_wrong_sequence_hits_both_parsers() -> None:
    path = builder.GMPY2_EXTENSION_PATH
    offsets = _command_offsets(REAL_RUNTIME_BYTES[path])
    mutated = _patch_u32(REAL_RUNTIME_BYTES[path], offsets[7], 0x2A)
    _assert_both_parsers_reject("gmpy2_extension", mutated)
    _assert_public_rejects(path, mutated)


def test_dylinker_wrong_placement_hits_both_parsers() -> None:
    path = builder.GMPY2_EXTENSION_PATH
    offsets = _command_offsets(REAL_RUNTIME_BYTES[path])
    mutated = _patch_u32(REAL_RUNTIME_BYTES[path], offsets[10], builder.LC_LOAD_DYLINKER)
    _assert_both_parsers_reject("gmpy2_extension", mutated)
    _assert_public_rejects(path, mutated)


def test_dylinker_multiplicity_hits_both_parsers() -> None:
    path = builder.PYTHON_PATH
    offsets = _command_offsets(REAL_RUNTIME_BYTES[path])
    mutated = _patch_u32(REAL_RUNTIME_BYTES[path], offsets[14], builder.LC_LOAD_DYLINKER)
    _assert_both_parsers_reject("python_executable", mutated)
    _assert_public_rejects(path, mutated)


def test_alias_duplicate_numerical_target_hits_both_classifiers() -> None:
    edges = [
        {
            "command": "LC_LOAD_DYLIB",
            "command_index": 10,
            "load_path": builder.GMP_PATH,
        },
        {
            "command": "LC_LOAD_DYLIB",
            "command_index": 11,
            "load_path": "@loader_path/../gmpy2.libs/libmpfr.6.dylib",
        },
        {
            "command": "LC_LOAD_DYLIB",
            "command_index": 12,
            "load_path": "@loader_path/../gmpy2.libs/libgmp.10.dylib",
        },
        {
            "command": "LC_LOAD_DYLIB",
            "command_index": 13,
            "load_path": "/usr/lib/libSystem.B.dylib",
        },
    ]
    _assert_both_classifiers_reject("gmpy2_extension", edges)


def test_unpinned_internal_edge_hits_both_classifiers() -> None:
    edges = [
        {
            "command": "LC_LOAD_DYLIB",
            "command_index": 10,
            "load_path": LITERAL_AUTHORITY_ROOT + "/site-packages/libExtra.dylib",
        }
    ]
    _assert_both_classifiers_reject("gmpy2_extension", edges)


def test_path_cap_hits_both_classifiers() -> None:
    edges = [
        {
            "command": "LC_LOAD_DYLIB",
            "command_index": 10,
            "load_path": "/" + "a" * (builder.MAX_PATH_CHARS + 1),
        }
    ]
    _assert_both_classifiers_reject("gmpy2_extension", edges)


def test_runtime_file_caps_hit_parsers_builder_and_validator() -> None:
    oversized_native = b"\xcf\xfa\xed\xfe" + b"\0" * (builder.MAX_RUNTIME_FILE_BYTES)
    _assert_both_parsers_reject("gmpy2_extension", oversized_native)
    _assert_public_rejects(builder.GMPY2_EXTENSION_PATH, oversized_native)

    raw, files = _inventory()
    files[builder.GMPY2_WRAPPER_PATH] = b"x" * (builder.MAX_RUNTIME_FILE_BYTES + 1)
    with pytest.raises(builder.RuntimeAuthorityBuildFailure):
        builder.build_runtime_authority(files)
    with pytest.raises(validator.RuntimeAuthorityValidationFailure):
        validator.validate_runtime_authority(raw, files)


@pytest.mark.parametrize("fat64", [False, True])
def test_mixed_fat_subtype_hits_both_parsers(fat64: bool) -> None:
    raw = _fat_wrap(
        REAL_RUNTIME_BYTES[builder.GMPY2_EXTENSION_PATH],
        fat64=fat64,
        table_subtype=1,
    )
    _assert_both_parsers_reject("gmpy2_extension", raw)
    _assert_public_rejects(builder.GMPY2_EXTENSION_PATH, raw)


def test_fat64_nonzero_reserved_hits_both_parsers() -> None:
    raw = _fat_wrap(
        REAL_RUNTIME_BYTES[builder.GMPY2_EXTENSION_PATH],
        fat64=True,
        reserved=1,
    )
    _assert_both_parsers_reject("gmpy2_extension", raw)
    _assert_public_rejects(builder.GMPY2_EXTENSION_PATH, raw)


def test_fat_table_and_selected_slice_mixed_subtype_hits_both_parsers() -> None:
    inner = _patch_u32(
        REAL_RUNTIME_BYTES[builder.GMPY2_EXTENSION_PATH],
        8,
        1,
    )
    raw = _fat_wrap(inner, fat64=False, table_subtype=0)
    _assert_both_parsers_reject("gmpy2_extension", raw)


@pytest.mark.parametrize(
    "mutator",
    [
        lambda raw: raw[:20],
        lambda raw: _patch_u32(raw, _command_offsets(raw)[0] + 4, 0),
        lambda raw: _patch_u32(raw, _command_offsets(raw)[0] + 4, 7),
        lambda raw: _patch_u32(raw, _command_offsets(raw)[0] + 4, 0xFFFFFFF8),
    ],
)
def test_truncation_and_command_size_mutations_hit_both_parsers(
    mutator: Callable[[bytes], bytes],
) -> None:
    path = builder.GMPY2_EXTENSION_PATH
    mutated = mutator(REAL_RUNTIME_BYTES[path])
    _assert_both_parsers_reject("gmpy2_extension", mutated)
    _assert_public_rejects(path, mutated)


def test_separate_parser_implementations_are_not_the_same_function_object() -> None:
    assert builder._parse_macho is not validator._parse_macho
    assert builder.RuntimeAuthorityBuildFailure is not (validator.RuntimeAuthorityValidationFailure)


def test_no_result_output_probe_or_runtime_closure_hash_fields_exist() -> None:
    raw, files = _inventory()
    validator.validate_runtime_authority(raw, files)
    text = raw.decode("ascii")
    for forbidden in (
        "result_sha256",
        "output_sha256",
        "receipt_sha256",
        "probe_ack_sha256",
        "runtime_closure_sha256",
    ):
        assert forbidden not in text
