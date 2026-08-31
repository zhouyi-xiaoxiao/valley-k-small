from __future__ import annotations

import hashlib

import continuum_c1_n0_runtime_import_closure_v1 as resolver
import pytest

REPORT_ROOT = "/report"


def _record(
    name: str,
    origin: str,
    path: str | None,
    raw: bytes | None,
) -> dict[str, object]:
    return {
        "import_name": name,
        "origin_kind": origin,
        "path": path,
        "sha256": None if raw is None else hashlib.sha256(raw).hexdigest(),
    }


def _resolve(
    entries: list[tuple[dict[str, object], bytes | None]],
    roots: list[object],
    packages: set[str] | frozenset[str] | object,
    member_kinds: dict[str, str] | None = None,
) -> tuple[resolver.ClosureRecord, ...]:
    records = [record for record, _raw in entries]
    sources = {
        record["path"]: raw
        for record, raw in entries
        if raw is not None and type(record["path"]) is str
    }
    return resolver.resolve_closure(
        records,
        roots,
        sources,
        packages,
        {} if member_kinds is None else member_kinds,
        report_root=REPORT_ROOT,
    )


def test_caller_bytes_are_used_without_reading_declared_paths() -> None:
    raw = b"TOKEN = 1\n"
    closure = _resolve(
        [
            (
                _record(
                    "nonexistent",
                    resolver.ORIGIN_REPORT_LOCAL,
                    "/report/code/nonexistent.py",
                    raw,
                ),
                raw,
            )
        ],
        ["nonexistent"],
        set(),
    )
    assert closure[0].sha256 == hashlib.sha256(raw).hexdigest()


def test_absolute_and_relative_imports_use_context_and_package_set() -> None:
    package_raw = b"import pkg.helper\n"
    helper_raw = b"from .sub import value\nimport pkg.sibling\n"
    sub_raw = b"value = 1\n"
    sibling_raw = b"TOKEN = 1\n"
    closure = _resolve(
        [
            (
                _record(
                    "pkg",
                    resolver.ORIGIN_RUNTIME_PREFIX,
                    "/runtime/pkg/__init__.py",
                    package_raw,
                ),
                package_raw,
            ),
            (
                _record(
                    "pkg.helper",
                    resolver.ORIGIN_RUNTIME_PREFIX,
                    "/runtime/pkg/helper.py",
                    helper_raw,
                ),
                helper_raw,
            ),
            (
                _record(
                    "pkg.sibling",
                    resolver.ORIGIN_RUNTIME_PREFIX,
                    "/runtime/pkg/sibling.py",
                    sibling_raw,
                ),
                sibling_raw,
            ),
            (
                _record(
                    "pkg.sub",
                    resolver.ORIGIN_RUNTIME_PREFIX,
                    "/runtime/pkg/sub.py",
                    sub_raw,
                ),
                sub_raw,
            ),
        ],
        ["pkg"],
        {"pkg"},
    )
    assert [record.import_name for record in closure] == [
        "pkg",
        "pkg.helper",
        "pkg.sibling",
        "pkg.sub",
    ]


def test_nonpackage_from_import_is_an_attribute_not_an_invented_module() -> None:
    root_raw = b"from support import value\n"
    support_raw = b"value = 1\n"
    closure = _resolve(
        [
            (
                _record(
                    "root",
                    resolver.ORIGIN_REPORT_LOCAL,
                    "/report/code/root.py",
                    root_raw,
                ),
                root_raw,
            ),
            (
                _record(
                    "support",
                    resolver.ORIGIN_REPORT_LOCAL,
                    "/report/code/support.py",
                    support_raw,
                ),
                support_raw,
            ),
        ],
        ["root"],
        set(),
    )
    assert {record.import_name for record in closure} == {"root", "support"}


def test_runtime_package_member_without_classification_is_rejected() -> None:
    root_raw = b"from pkg import missing\n"
    package_raw = b"TOKEN = 1\n"
    with pytest.raises(
        resolver.ImportClosureFailure,
        match="classification missing",
    ):
        _resolve(
            [
                (
                    _record(
                        "pkg",
                        resolver.ORIGIN_RUNTIME_PREFIX,
                        "/runtime/pkg/__init__.py",
                        package_raw,
                    ),
                    package_raw,
                ),
                (
                    _record(
                        "root",
                        resolver.ORIGIN_RUNTIME_PREFIX,
                        "/runtime/root.py",
                        root_raw,
                    ),
                    root_raw,
                ),
            ],
            ["root"],
            {"pkg"},
        )


def test_package_attribute_submodule_classification_collision_is_rejected() -> None:
    with pytest.raises(
        resolver.ImportClosureFailure,
        match="attribute/module collision",
    ):
        resolver.resolve_imports(
            b"from pkg import member\n",
            "root",
            {"pkg", "pkg.member", "root"},
            {"pkg"},
            {"pkg.member": "attribute"},
            resolver.RUNTIME_PREFIX_PROFILE,
            is_package=False,
        )


def test_package_dunder_getattr_does_not_resolve_member_ambiguity() -> None:
    package_raw = b"def __getattr__(name):\n    return name\n"
    root_raw = b"from pkg import dynamic\n"
    with pytest.raises(
        resolver.ImportClosureFailure,
        match="classification missing",
    ):
        _resolve(
            [
                (
                    _record(
                        "pkg",
                        resolver.ORIGIN_RUNTIME_PREFIX,
                        "/runtime/pkg/__init__.py",
                        package_raw,
                    ),
                    package_raw,
                ),
                (
                    _record(
                        "root",
                        resolver.ORIGIN_RUNTIME_PREFIX,
                        "/runtime/root.py",
                        root_raw,
                    ),
                    root_raw,
                ),
            ],
            ["root"],
            {"pkg"},
        )


def test_strict_package_member_is_forbidden_even_when_classified() -> None:
    with pytest.raises(resolver.ImportClosureFailure, match="strict profile"):
        resolver.resolve_imports(
            b"from pkg import member\n",
            "root",
            {"pkg", "pkg.member", "root"},
            {"pkg"},
            {"pkg.member": "module"},
            resolver.STRICT_PROFILE,
            is_package=False,
        )


def test_runtime_re_style_package_submodules_use_exact_classifications() -> None:
    package_raw = b"from . import _compiler, _parser\n"
    compiler_raw = b"TOKEN = 1\n"
    parser_raw = b"TOKEN = 2\n"
    closure = _resolve(
        [
            (
                _record(
                    "re",
                    resolver.ORIGIN_RUNTIME_PREFIX,
                    "/runtime/re/__init__.py",
                    package_raw,
                ),
                package_raw,
            ),
            (
                _record(
                    "re._compiler",
                    resolver.ORIGIN_RUNTIME_PREFIX,
                    "/runtime/re/_compiler.py",
                    compiler_raw,
                ),
                compiler_raw,
            ),
            (
                _record(
                    "re._parser",
                    resolver.ORIGIN_RUNTIME_PREFIX,
                    "/runtime/re/_parser.py",
                    parser_raw,
                ),
                parser_raw,
            ),
        ],
        ["re"],
        {"re"},
        {"re._compiler": "module", "re._parser": "module"},
    )
    assert [record.import_name for record in closure] == [
        "re",
        "re._compiler",
        "re._parser",
    ]


def test_runtime_package_attribute_classification_adds_only_base() -> None:
    imports = resolver.resolve_imports(
        b"from pkg import VERSION\n",
        "root",
        {"pkg", "root"},
        {"pkg"},
        {"pkg.VERSION": "attribute"},
        resolver.RUNTIME_PREFIX_PROFILE,
        is_package=False,
    )
    assert imports == frozenset({"pkg"})


def test_package_member_classification_missing_module_extra_and_invalid_hold() -> None:
    source = b"from pkg import child\n"
    with pytest.raises(resolver.ImportClosureFailure, match="lacks declaration"):
        resolver.resolve_imports(
            source,
            "root",
            {"pkg", "root"},
            {"pkg"},
            {"pkg.child": "module"},
            resolver.RUNTIME_PREFIX_PROFILE,
            is_package=False,
        )
    with pytest.raises(resolver.ImportClosureFailure, match="unused"):
        resolver.resolve_imports(
            b"TOKEN = 1\n",
            "root",
            {"pkg", "root"},
            {"pkg"},
            {"pkg.extra": "attribute"},
            resolver.RUNTIME_PREFIX_PROFILE,
            is_package=False,
        )
    with pytest.raises(resolver.ImportClosureFailure, match="module or attribute"):
        resolver.resolve_imports(
            source,
            "root",
            {"pkg", "root"},
            {"pkg"},
            {"pkg.child": True},
            resolver.RUNTIME_PREFIX_PROFILE,
            is_package=False,
        )


def test_every_dotted_parent_record_and_package_declaration_is_required() -> None:
    child_raw = b"TOKEN = 1\n"
    with pytest.raises(resolver.ImportClosureFailure, match="parent prefixes"):
        _resolve(
            [
                (
                    _record(
                        "pkg.child",
                        resolver.ORIGIN_RUNTIME_PREFIX,
                        "/runtime/pkg/child.py",
                        child_raw,
                    ),
                    child_raw,
                )
            ],
            ["pkg.child"],
            set(),
        )


def test_dead_and_platform_conditional_imports_are_conservatively_included() -> None:
    root_raw = (
        b"if False:\n    import dead\n"
        b"if sys.platform == 'never':\n    import platform_only\n"
        b"import sys\n"
    )
    dead_raw = b"TOKEN = 1\n"
    platform_raw = b"TOKEN = 2\n"
    closure = _resolve(
        [
            (
                _record(
                    "dead",
                    resolver.ORIGIN_RUNTIME_PREFIX,
                    "/runtime/dead.py",
                    dead_raw,
                ),
                dead_raw,
            ),
            (
                _record(
                    "platform_only",
                    resolver.ORIGIN_RUNTIME_PREFIX,
                    "/runtime/platform_only.py",
                    platform_raw,
                ),
                platform_raw,
            ),
            (
                _record(
                    "root",
                    resolver.ORIGIN_REPORT_LOCAL,
                    "/report/code/root.py",
                    root_raw,
                ),
                root_raw,
            ),
            (_record("sys", resolver.ORIGIN_BUILTIN, None, None), None),
        ],
        ["root"],
        set(),
    )
    assert len(closure) == 4


def test_builtin_frozen_and_native_records_are_supported() -> None:
    root_raw = b"import builtin_mod\nimport frozen_mod\nimport native\n"
    native_raw = b"\x7fNATIVE"
    closure = _resolve(
        [
            (
                _record(
                    "root",
                    resolver.ORIGIN_REPORT_LOCAL,
                    "/report/code/root.py",
                    root_raw,
                ),
                root_raw,
            ),
            (_record("builtin_mod", resolver.ORIGIN_BUILTIN, None, None), None),
            (_record("frozen_mod", resolver.ORIGIN_FROZEN, None, None), None),
            (
                _record(
                    "native",
                    resolver.ORIGIN_NATIVE,
                    "/runtime/native.cpython-312-darwin.so",
                    native_raw,
                ),
                native_raw,
            ),
        ],
        ["root"],
        set(),
    )
    assert {record.origin_kind for record in closure} == {
        resolver.ORIGIN_REPORT_LOCAL,
        resolver.ORIGIN_BUILTIN,
        resolver.ORIGIN_FROZEN,
        resolver.ORIGIN_NATIVE,
    }


def test_runtime_prefix_cpython_extension_is_an_opaque_terminal() -> None:
    root_raw = b"import _hashlib\n"
    extension_raw = b"\xff\x00NOT_UTF8_CPYTHON_EXTENSION"
    closure = _resolve(
        [
            (
                _record(
                    "root",
                    resolver.ORIGIN_REPORT_LOCAL,
                    "/report/code/root.py",
                    root_raw,
                ),
                root_raw,
            ),
            (
                _record(
                    "_hashlib",
                    resolver.ORIGIN_RUNTIME_PREFIX,
                    "/runtime/lib-dynload/_hashlib.cpython-312-darwin.so",
                    extension_raw,
                ),
                extension_raw,
            ),
        ],
        ["root"],
        set(),
    )
    assert [record.import_name for record in closure] == ["_hashlib", "root"]


def test_runtime_prefix_sourceless_pyc_is_rejected() -> None:
    raw = b"\x00PYC"
    with pytest.raises(resolver.ImportClosureFailure, match=r"\.py or opaque \.so"):
        _resolve(
            [
                (
                    _record(
                        "cache",
                        resolver.ORIGIN_RUNTIME_PREFIX,
                        "/runtime/cache.pyc",
                        raw,
                    ),
                    raw,
                )
            ],
            ["cache"],
            set(),
        )


def test_reachable_cycle_is_accepted_but_disconnected_cycle_is_rejected() -> None:
    a_raw = b"import b\n"
    b_raw = b"import a\n"
    root_raw = b"TOKEN = 0\n"
    reachable = _resolve(
        [
            (
                _record(
                    "a",
                    resolver.ORIGIN_REPORT_LOCAL,
                    "/report/code/a.py",
                    a_raw,
                ),
                a_raw,
            ),
            (
                _record(
                    "b",
                    resolver.ORIGIN_REPORT_LOCAL,
                    "/report/code/b.py",
                    b_raw,
                ),
                b_raw,
            ),
        ],
        ["a"],
        set(),
    )
    assert [record.import_name for record in reachable] == ["a", "b"]
    with pytest.raises(resolver.ImportClosureFailure, match="unreachable"):
        _resolve(
            [
                (
                    _record(
                        "a",
                        resolver.ORIGIN_REPORT_LOCAL,
                        "/report/code/a.py",
                        a_raw,
                    ),
                    a_raw,
                ),
                (
                    _record(
                        "b",
                        resolver.ORIGIN_REPORT_LOCAL,
                        "/report/code/b.py",
                        b_raw,
                    ),
                    b_raw,
                ),
                (
                    _record(
                        "root",
                        resolver.ORIGIN_REPORT_LOCAL,
                        "/report/code/root.py",
                        root_raw,
                    ),
                    root_raw,
                ),
            ],
            ["root"],
            set(),
        )


@pytest.mark.parametrize(
    "source",
    [
        b"__import__('x')\n",
        b"from builtins import eval as e\ne('1')\n",
        b"import builtins as b\nf = b.eval\n",
        b"import importlib\nf = importlib.import_module\n",
        b"from importlib import import_module as load\n",
        b"import importlib.util\nimportlib.util.find_spec('x')\n",
        b"from importlib.util import module_from_spec\n",
        b"import importlib.util as u\nu.spec_from_file_location('x', 'y')\n",
        b"from importlib.machinery import SourceFileLoader\n",
        b"from .danger import SourceFileLoader\n",
        b"from importlib.machinery import SourcelessFileLoader as Loader\n",
        b"import importlib.machinery as machinery\nmachinery.ExtensionFileLoader\n",
        b"import importlib.machinery as machinery\nmachinery.FileFinder\n",
        b"import importlib.machinery as machinery\nmachinery.PathFinder\n",
        b"import importlib.machinery as machinery\nmachinery.BuiltinImporter\n",
        b"import importlib.machinery as machinery\nmachinery.FrozenImporter\n",
        b"loader.exec_module(module)\n",
        b"loader.load_module('x')\n",
        b"loader.create_module(spec)\n",
        b"import sys\nsys.modules['x']\n",
        b"import sys\nsys.meta_path\n",
        b"import sys\nsys.path\n",
        b"from sys import path as search_path\n",
        b"import sys\nstate = sys\nstate.modules['x']\n",
        b"__builtins__['eval']\n",
        b"value = __loader__\n",
        b"value = __spec__\n",
        b"def __getattr__(name):\n    return name\n",
        b"import runpy\n",
        b"import pkgutil\n",
        b"import zipimport\n",
        b"globals()['__builtins__']\n",
        b"import importlib\ngetattr(importlib, name)\n",
        b"import builtins\nlookup = builtins.getattr\nlookup(importlib, name)\n",
        b"import importlib\ngetattr(importlib, 'import_' + 'module')\n",
        b"import operator\noperator.attrgetter(name)(importlib)\n",
        b"obj.__dict__['safe']\n",
    ],
)
def test_reproduced_dynamic_loading_reflection_evasions_are_rejected(
    source: bytes,
) -> None:
    with pytest.raises(resolver.ImportClosureFailure):
        resolver.resolve_imports(
            source,
            "root",
            {"root", "builtins", "importlib", "importlib.util", "sys"},
            {"importlib"},
            {},
            resolver.STRICT_PROFILE,
            is_package=False,
        )


def test_benign_regex_compile_attributes_and_constant_getattr_are_allowed() -> None:
    source = (
        b"import re\n"
        b"pattern = re.compile('x')\n"
        b"value = thing.compile\n"
        b"other = thing.safe_attribute\n"
        b"third = getattr(thing, 'safe_name')\n"
    )
    assert resolver.resolve_imports(
        source,
        "root",
        {"re", "root"},
        set(),
        {},
        resolver.STRICT_PROFILE,
        is_package=False,
    ) == frozenset({"re"})


def test_module_alias_taints_are_monotone_and_do_not_oscillate() -> None:
    imports = resolver.resolve_imports(
        b"import builtins as a\nimport sys as b\nx = a\nx = b\nTOKEN = 1\n",
        "root",
        {"builtins", "root", "sys"},
        set(),
        {},
        resolver.RUNTIME_PREFIX_PROFILE,
        is_package=False,
    )
    assert imports == frozenset({"builtins", "sys"})


def test_runtime_profile_allows_generic_reflection_needed_by_stdlib() -> None:
    source = (
        b"def __getattr__(name):\n    return name\n"
        b"value = getattr(object_value, attribute_name, None)\n"
        b"namespace = locals()\n"
        b"mapping = object_value.__dict__\n"
        b"getter = object_value.__getattribute__\n"
        b"exec(code, namespace)\n"
    )
    assert (
        resolver.resolve_imports(
            source,
            "runtime_mod",
            {"runtime_mod"},
            set(),
            {},
            resolver.RUNTIME_PREFIX_PROFILE,
            is_package=False,
        )
        == frozenset()
    )
    with pytest.raises(resolver.ImportClosureFailure):
        resolver.resolve_imports(
            source,
            "strict_mod",
            {"strict_mod"},
            set(),
            {},
            resolver.STRICT_PROFILE,
            is_package=False,
        )


def test_runtime_profile_allows_subprocess_style_builtins_reflection() -> None:
    imports = resolver.resolve_imports(
        b"import builtins\nvalue = getattr(builtins, dynamic_name)\n",
        "runtime_mod",
        {"builtins", "runtime_mod"},
        set(),
        {},
        resolver.RUNTIME_PREFIX_PROFILE,
        is_package=False,
    )
    assert imports == frozenset({"builtins"})


def test_runtime_profile_allows_subprocess_style_sys_flags_reflection() -> None:
    imports = resolver.resolve_imports(
        b"import sys\nvalue = getattr(sys.flags, dynamic_name)\n",
        "runtime_mod",
        {"runtime_mod", "sys"},
        set(),
        {},
        resolver.RUNTIME_PREFIX_PROFILE,
        is_package=False,
    )
    assert imports == frozenset({"sys"})


@pytest.mark.parametrize(
    "source",
    [
        b"__import__('x')\n",
        b"import importlib\nimportlib.import_module('x')\n",
        b"import runpy\n",
        b"loader.exec_module(module)\n",
        b"import sys\nsys.modules['x']\n",
        b"from importlib.machinery import SourceFileLoader\n",
    ],
)
def test_runtime_profile_still_rejects_actual_import_loading_machinery(
    source: bytes,
) -> None:
    with pytest.raises(resolver.ImportClosureFailure):
        resolver.resolve_imports(
            source,
            "runtime_mod",
            {"importlib", "runtime_mod", "sys"},
            {"importlib"},
            {},
            resolver.RUNTIME_PREFIX_PROFILE,
            is_package=False,
        )


@pytest.mark.parametrize(
    "source",
    [
        b"import importlib\ngetattr(importlib, name)\n",
        b"import importlib\ngetattr(importlib.util, name)\n",
        b"import importlib\nalias = importlib\ngetattr(alias, name)\n",
        b"import sys\ngetattr(sys, name)\n",
    ],
)
def test_runtime_nonconstant_getattr_on_import_state_is_rejected(
    source: bytes,
) -> None:
    with pytest.raises(resolver.ImportClosureFailure, match="nonconstant getattr"):
        resolver.resolve_imports(
            source,
            "runtime_mod",
            {"builtins", "importlib", "runtime_mod", "sys"},
            {"importlib"},
            {},
            resolver.RUNTIME_PREFIX_PROFILE,
            is_package=False,
        )


@pytest.mark.parametrize(
    "profile",
    [resolver.STRICT_PROFILE, resolver.RUNTIME_PREFIX_PROFILE],
)
def test_harmless_docstrings_and_free_strings_are_not_execution(profile: str) -> None:
    source = (
        b'"""Documentation may say compile or importlib without executing it."""\n'
        b"text = 'import_' + 'module'\n"
    )
    assert (
        resolver.resolve_imports(
            source,
            "documented_mod",
            {"documented_mod"},
            set(),
            {},
            profile,
            is_package=False,
        )
        == frozenset()
    )


def test_strict_profile_wildcard_is_rejected() -> None:
    with pytest.raises(resolver.ImportClosureFailure, match="wildcard"):
        resolver.resolve_imports(
            b"from support import *\n",
            "root",
            {"root", "support"},
            set(),
            {},
            resolver.STRICT_PROFILE,
            is_package=False,
        )


def test_runtime_profile_package_base_wildcard_is_rejected() -> None:
    with pytest.raises(resolver.ImportClosureFailure, match="wildcard"):
        resolver.resolve_imports(
            b"from pkg import *\n",
            "root",
            {"pkg", "root"},
            {"pkg"},
            {},
            resolver.RUNTIME_PREFIX_PROFILE,
            is_package=False,
        )


def test_gmpy2_wrapper_runtime_wildcard_to_native_module_is_accepted() -> None:
    wrapper_raw = b"from .gmpy2 import *\n"
    native_raw = b"\x7fGMPY2_NATIVE"
    closure = _resolve(
        [
            (
                _record(
                    "gmpy2",
                    resolver.ORIGIN_RUNTIME_PREFIX,
                    "/runtime/gmpy2/__init__.py",
                    wrapper_raw,
                ),
                wrapper_raw,
            ),
            (
                _record(
                    "gmpy2.gmpy2",
                    resolver.ORIGIN_NATIVE,
                    "/runtime/gmpy2/gmpy2.cpython-312-darwin.so",
                    native_raw,
                ),
                native_raw,
            ),
        ],
        ["gmpy2"],
        {"gmpy2"},
    )
    assert [record.import_name for record in closure] == ["gmpy2", "gmpy2.gmpy2"]


@pytest.mark.parametrize(
    "bad_path",
    [
        "report/code/root.py",
        "/report/code/../root.py",
        "/report//code/root.py",
        "//report/code/root.py",
        "/report/symlink/../code/root.py",
        "/report/code/root.py/",
    ],
)
def test_symlink_like_and_noncanonical_path_strings_are_rejected(
    bad_path: str,
) -> None:
    raw = b"TOKEN = 1\n"
    with pytest.raises(resolver.ImportClosureFailure, match="canonical|noncanonical"):
        resolver.resolve_closure(
            [_record("root", resolver.ORIGIN_REPORT_LOCAL, bad_path, raw)],
            ["root"],
            {bad_path: raw},
            set(),
            {},
            report_root=REPORT_ROOT,
        )


def test_sha_mismatch_and_extra_source_bytes_are_rejected() -> None:
    raw = b"TOKEN = 1\n"
    record = _record(
        "root",
        resolver.ORIGIN_REPORT_LOCAL,
        "/report/code/root.py",
        raw,
    )
    record["sha256"] = "0" * 64
    with pytest.raises(resolver.ImportClosureFailure, match="SHA-256 mismatch"):
        resolver.resolve_closure(
            [record],
            ["root"],
            {"/report/code/root.py": raw},
            set(),
            {},
            report_root=REPORT_ROOT,
        )
    record["sha256"] = hashlib.sha256(raw).hexdigest()
    with pytest.raises(resolver.ImportClosureFailure, match="exactly equal"):
        resolver.resolve_closure(
            [record],
            ["root"],
            {
                "/report/code/root.py": raw,
                "/runtime/unbound.py": b"TOKEN = 2\n",
            },
            set(),
            {},
            report_root=REPORT_ROOT,
        )


def test_missing_source_bytes_duplicate_path_and_nonlowercase_sha_are_rejected() -> None:
    raw = b"TOKEN = 1\n"
    path = "/report/code/shared.py"
    record = _record("shared", resolver.ORIGIN_REPORT_LOCAL, path, raw)
    with pytest.raises(resolver.ImportClosureFailure, match="no caller-supplied bytes"):
        resolver.resolve_closure(
            [record],
            ["shared"],
            {},
            set(),
            {},
            report_root=REPORT_ROOT,
        )

    bad_sha = dict(record)
    bad_sha["sha256"] = "A" * 64
    with pytest.raises(resolver.ImportClosureFailure, match="lowercase SHA-256"):
        resolver.resolve_closure(
            [bad_sha],
            ["shared"],
            {path: raw},
            set(),
            {},
            report_root=REPORT_ROOT,
        )

    with pytest.raises(resolver.ImportClosureFailure, match="multiple import names"):
        resolver.resolve_closure(
            [
                _record("pkg", resolver.ORIGIN_BUILTIN, None, None),
                record,
                _record("pkg.shared", resolver.ORIGIN_REPORT_LOCAL, path, raw),
            ],
            ["shared"],
            {path: raw},
            {"pkg"},
            {},
            report_root=REPORT_ROOT,
        )


def test_closure_output_is_deterministic_for_shuffled_records_and_byte_keys() -> None:
    root_raw = b"import b\nimport a\n"
    a_raw = b"TOKEN = 'a'\n"
    b_raw = b"TOKEN = 'b'\n"
    records = [
        _record("b", resolver.ORIGIN_REPORT_LOCAL, "/report/code/b.py", b_raw),
        _record("root", resolver.ORIGIN_REPORT_LOCAL, "/report/code/root.py", root_raw),
        _record("a", resolver.ORIGIN_REPORT_LOCAL, "/report/code/a.py", a_raw),
    ]
    first = resolver.resolve_closure(
        records,
        ["root"],
        {
            "/report/code/b.py": b_raw,
            "/report/code/root.py": root_raw,
            "/report/code/a.py": a_raw,
        },
        set(),
        {},
        report_root=REPORT_ROOT,
    )
    second = resolver.resolve_closure(
        list(reversed(records)),
        ["root"],
        {
            "/report/code/a.py": a_raw,
            "/report/code/root.py": root_raw,
            "/report/code/b.py": b_raw,
        },
        set(),
        {},
        report_root=REPORT_ROOT,
    )
    assert first == second
    assert [record.import_name for record in first] == ["a", "b", "root"]


def test_file_package_path_and_independent_package_set_must_agree() -> None:
    raw = b"TOKEN = 1\n"
    with pytest.raises(resolver.ImportClosureFailure, match="package declaration"):
        _resolve(
            [
                (
                    _record(
                        "pkg",
                        resolver.ORIGIN_RUNTIME_PREFIX,
                        "/runtime/pkg/__init__.py",
                        raw,
                    ),
                    raw,
                )
            ],
            ["pkg"],
            set(),
        )


@pytest.mark.parametrize(
    ("origin", "path"),
    [
        (resolver.ORIGIN_REPORT_LOCAL, "/runtime/root.py"),
        (resolver.ORIGIN_RUNTIME_PREFIX, "/report/code/root.py"),
        (resolver.ORIGIN_NATIVE, "/report/code/root.so"),
    ],
)
def test_lexical_report_root_reclassification_is_rejected(
    origin: str,
    path: str,
) -> None:
    raw = b"TOKEN = 1\n"
    with pytest.raises(resolver.ImportClosureFailure, match="outside|reclassified"):
        resolver.resolve_closure(
            [_record("root", origin, path, raw)],
            ["root"],
            {path: raw},
            set(),
            {},
            report_root=REPORT_ROOT,
        )


def test_source_byte_cap_is_enforced_before_parsing() -> None:
    with pytest.raises(resolver.ImportClosureFailure, match="source byte cap"):
        resolver.resolve_imports(
            b"#" * (resolver.MAX_SOURCE_BYTES + 1),
            "root",
            {"root"},
            set(),
            {},
            resolver.STRICT_PROFILE,
            is_package=False,
        )


@pytest.mark.parametrize(
    "source",
    [
        b"x = '\x00'\n",
        b"(" * 5_000 + b"0" + b")" * 5_000,
    ],
)
def test_parser_pathologies_are_normalized_to_protocol_failure(
    source: bytes,
) -> None:
    with pytest.raises(
        resolver.ImportClosureFailure,
        match="parser/scanner rejected pathological input",
    ):
        resolver.resolve_imports(
            source,
            "root",
            {"root"},
            set(),
            {},
            resolver.STRICT_PROFILE,
            is_package=False,
        )


@pytest.mark.parametrize(
    ("mutation", "packages", "roots"),
    [
        (
            {
                "import_name": "root",
                "origin_kind": "builtin",
                "path": None,
                "sha256": False,
            },
            set(),
            ["root"],
        ),
        (
            {
                "import_name": "root",
                "origin_kind": 1,
                "path": None,
                "sha256": None,
            },
            set(),
            ["root"],
        ),
        (
            {
                "import_name": "root",
                "origin_kind": "builtin",
                "path": None,
                "sha256": None,
            },
            [],
            ["root"],
        ),
        (
            {
                "import_name": "root",
                "origin_kind": "builtin",
                "path": None,
                "sha256": None,
            },
            set(),
            [True],
        ),
    ],
)
def test_exact_schema_and_bool_int_confusion_are_rejected(
    mutation: dict[str, object],
    packages: object,
    roots: list[object],
) -> None:
    with pytest.raises(resolver.ImportClosureFailure):
        resolver.resolve_closure(
            [mutation],
            roots,
            {},
            packages,
            {},
            report_root=REPORT_ROOT,
        )
