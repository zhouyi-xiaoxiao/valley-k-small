"""Authenticated-by-caller, AST-only Python import-closure resolution.

This helper performs only syntactic import analysis.  It never opens, stats,
resolves, imports, or executes a declared path.  The caller supplies immutable
source bytes under exact canonical absolute path strings and remains
responsible for authenticating file identity, symlink freedom, path provenance,
and origin classification.  This module checks byte SHA-256 joins and, when a
report root is supplied, lexical origin containment only.

Runtime package-member classifications are separately supplied by the trusted
adapter/origin probe.  They are not candidate-result data.

The restricted-source scan closes known static-analysis evasions.  It is not a
Python sandbox and must not be represented as one.
"""

from __future__ import annotations

import ast
import dataclasses
import hashlib
import pathlib
import re
import typing

STRICT_PROFILE = "candidate_report_local_strict_v1"
RUNTIME_PREFIX_PROFILE = "runtime_prefix_static_v1"

ORIGIN_BUILTIN = "builtin"
ORIGIN_FROZEN = "frozen"
ORIGIN_REPORT_LOCAL = "file_report_local"
ORIGIN_RUNTIME_PREFIX = "file_runtime_prefix"
ORIGIN_NATIVE = "numerical_native_extension"

MAX_SOURCE_BYTES = 8_000_000
MAX_FILE_BYTES = 67_108_864

_PROFILES = frozenset({STRICT_PROFILE, RUNTIME_PREFIX_PROFILE})
_ORIGINS = frozenset(
    {
        ORIGIN_BUILTIN,
        ORIGIN_FROZEN,
        ORIGIN_REPORT_LOCAL,
        ORIGIN_RUNTIME_PREFIX,
        ORIGIN_NATIVE,
    }
)
_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*\Z")
_SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
_RECORD_KEYS = frozenset({"import_name", "origin_kind", "path", "sha256"})
_PACKAGE_MEMBER_KINDS = frozenset({"attribute", "module"})
_DYNAMIC_MODULE_ROOTS = frozenset({"runpy", "pkgutil", "zipimport"})
_EXECUTION_BUILTIN_NAMES = frozenset({"__import__", "compile", "eval", "exec"})
_REFLECTION_BUILTIN_NAMES = frozenset({"globals", "locals", "vars", "setattr", "delattr"})
_DYNAMIC_BUILTIN_NAMES = _EXECUTION_BUILTIN_NAMES | _REFLECTION_BUILTIN_NAMES
_DYNAMIC_IMPORT_NAMES = frozenset(
    {
        "import_module",
        "find_spec",
        "module_from_spec",
        "spec_from_file_location",
        "spec_from_loader",
        "resolve_name",
        "run_module",
        "run_path",
        "zipimporter",
        "SourceFileLoader",
        "SourcelessFileLoader",
        "ExtensionFileLoader",
        "FileFinder",
        "PathFinder",
        "BuiltinImporter",
        "FrozenImporter",
        "__loader__",
        "__spec__",
        "__getattr__",
    }
)
_REFLECTION_HELPER_NAMES = frozenset({"attrgetter", "methodcaller"})
_DANGEROUS_GENERIC_ATTRIBUTES = frozenset(
    {
        "__builtins__",
        "__dict__",
        "__globals__",
        "__code__",
        "__closure__",
        "__bases__",
        "__subclasses__",
        "__getattribute__",
        "__import__",
        "import_module",
        "find_spec",
        "module_from_spec",
        "spec_from_file_location",
        "spec_from_loader",
        "exec_module",
        "load_module",
        "create_module",
        "run_module",
        "run_path",
        "resolve_name",
        "attrgetter",
        "methodcaller",
        "SourceFileLoader",
        "SourcelessFileLoader",
        "ExtensionFileLoader",
        "FileFinder",
        "PathFinder",
        "BuiltinImporter",
        "FrozenImporter",
        "__loader__",
        "__spec__",
        "__getattr__",
    }
)
_RUNTIME_LOADING_ATTRIBUTES = _DANGEROUS_GENERIC_ATTRIBUTES - frozenset(
    {
        "__dict__",
        "__globals__",
        "__code__",
        "__closure__",
        "__bases__",
        "__subclasses__",
        "__getattribute__",
        "attrgetter",
        "methodcaller",
    }
)
_DANGEROUS_SYS_ATTRIBUTES = frozenset(
    {"modules", "meta_path", "path", "path_hooks", "path_importer_cache"}
)
_DANGEROUS_INDIRECTION_NAMES = (
    _DYNAMIC_IMPORT_NAMES | _DANGEROUS_GENERIC_ATTRIBUTES | frozenset({"__builtins__"})
)
_RUNTIME_LOADING_INDIRECTION_NAMES = (
    _DYNAMIC_IMPORT_NAMES | _RUNTIME_LOADING_ATTRIBUTES | frozenset({"__builtins__", "__import__"})
)


class ImportClosureFailure(RuntimeError):
    """Fail-closed rejection of a malformed or incomplete static closure."""


@dataclasses.dataclass(frozen=True)
class ClosureRecord:
    """One SHA-joined declaration in a resolved import closure."""

    import_name: str
    origin_kind: str
    path: str | None
    sha256: str | None


def _fail(detail: str) -> typing.NoReturn:
    raise ImportClosureFailure(detail)


def _name(value: object, label: str) -> str:
    if type(value) is not str or _NAME_RE.fullmatch(value) is None:
        _fail(f"{label}: dotted Python import name required")
    return value


def _name_set(value: object, label: str) -> frozenset[str]:
    if type(value) not in {set, frozenset}:
        _fail(f"{label}: independently supplied set required")
    names = [_name(item, f"{label} item") for item in value]
    if len(names) != len(set(names)):
        _fail(f"{label}: duplicate import name")
    return frozenset(names)


def _package_member_classifications(value: object) -> dict[str, str]:
    if type(value) is not dict:
        _fail("package_member_kinds: exact classification object required")
    classifications: dict[str, str] = {}
    for raw_name, raw_kind in value.items():
        name = _name(raw_name, "package_member_kinds key")
        if type(raw_kind) is not str or raw_kind not in _PACKAGE_MEMBER_KINDS:
            _fail(f"package_member_kinds[{name}]: module or attribute required")
        classifications[name] = raw_kind
    return classifications


def _canonical_absolute_path(value: object, label: str) -> str:
    if type(value) is not str or not value.startswith("/") or value == "/":
        _fail(f"{label}: canonical absolute POSIX file path required")
    if "\x00" in value:
        _fail(f"{label}: NUL forbidden")
    if "//" in value:
        _fail(f"{label}: noncanonical absolute path")
    pure = pathlib.PurePosixPath(value)
    if str(pure) != value or any(part in {"", ".", ".."} for part in pure.parts[1:]):
        _fail(f"{label}: noncanonical absolute path")
    return value


def _lexically_within(path: str, root: str) -> bool:
    return path == root or path.startswith(root + "/")


def _prefixes(import_name: str) -> set[str]:
    parts = import_name.split(".")
    return {".".join(parts[:end]) for end in range(1, len(parts) + 1)}


def _resolve_from_base(
    node: ast.ImportFrom,
    module_name: str,
    is_package: bool,
) -> str:
    if node.level == 0:
        if node.module is None:
            _fail("absolute from-import has no module")
        return node.module
    package = module_name if is_package else module_name.rpartition(".")[0]
    if not package:
        _fail(f"{module_name}: relative import outside a package")
    parts = package.split(".")
    ascent = node.level - 1
    if ascent >= len(parts):
        _fail(f"{module_name}: relative import escapes its top-level package")
    prefix = parts[: len(parts) - ascent]
    if node.module:
        prefix.extend(node.module.split("."))
    return ".".join(prefix)


def _static_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and type(node.value) is str:
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _static_string(node.left)
        right = _static_string(node.right)
        if left is not None and right is not None:
            return left + right
    if isinstance(node, ast.JoinedStr):
        values: list[str] = []
        for value in node.values:
            text = _static_string(value)
            if text is None:
                return None
            values.append(text)
        return "".join(values)
    return None


def _contains_dangerous_token(text: str, names: frozenset[str]) -> bool:
    return any(
        re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])",
            text,
        )
        for token in names
    )


def _bound_import_aliases(
    tree: ast.Module,
    profile: str,
) -> tuple[dict[str, set[str]], set[str]]:
    modules: dict[str, set[str]] = {
        "builtins": {"builtins"},
        "importlib": {"importlib"},
        "sys": {"sys"},
    }
    getattr_aliases = {"getattr"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in _DYNAMIC_MODULE_ROOTS:
                    _fail(f"dynamic loading/execution module import forbidden: {alias.name}")
                if root == "sys" and any(
                    part in _DANGEROUS_SYS_ATTRIBUTES for part in alias.name.split(".")[1:]
                ):
                    _fail(f"dangerous sys import state forbidden: {alias.name}")
                if any(part in _DYNAMIC_IMPORT_NAMES for part in alias.name.split(".")):
                    _fail(f"dynamic machinery import/reference forbidden: {alias.name}")
                if profile == STRICT_PROFILE and any(
                    part in _REFLECTION_HELPER_NAMES for part in alias.name.split(".")
                ):
                    _fail(f"reflection machinery import forbidden: {alias.name}")
                bound = alias.asname or root
                modules.setdefault(bound, set()).add(alias.name if alias.asname else root)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if (
                    alias.name == "__import__"
                    or alias.name in _DYNAMIC_IMPORT_NAMES
                    or (
                        profile == STRICT_PROFILE
                        and (
                            alias.name in _DYNAMIC_BUILTIN_NAMES
                            or alias.name in _REFLECTION_HELPER_NAMES
                        )
                    )
                ):
                    _fail(
                        "dynamic machinery import/reference forbidden: "
                        f"{alias.asname or alias.name}"
                    )
            if node.level != 0 or node.module is None:
                continue
            root = node.module.split(".", 1)[0]
            if root in _DYNAMIC_MODULE_ROOTS:
                _fail(f"dynamic loading/execution module import forbidden: {node.module}")
            for alias in node.names:
                bound = alias.asname or alias.name
                if root == "sys" and alias.name in _DANGEROUS_SYS_ATTRIBUTES:
                    _fail(f"dangerous sys import state forbidden: {bound}")
                if node.module == "builtins" and alias.name == "getattr":
                    getattr_aliases.add(bound)
                modules.setdefault(bound, set()).add(f"{node.module}.{alias.name}")
    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                targets = node.targets
                value = node.value
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                targets = [node.target]
                value = node.value
            else:
                continue
            target_names = [target.id for target in targets if isinstance(target, ast.Name)]
            if isinstance(value, ast.Name) and value.id in modules:
                for target_name in target_names:
                    target_modules = modules.setdefault(target_name, set())
                    before = len(target_modules)
                    target_modules.update(modules[value.id])
                    if len(target_modules) != before:
                        changed = True
            if isinstance(value, ast.Name) and value.id in getattr_aliases:
                for target_name in target_names:
                    if target_name not in getattr_aliases:
                        getattr_aliases.add(target_name)
                        changed = True
            if (
                isinstance(value, ast.Attribute)
                and isinstance(value.value, ast.Name)
                and "builtins" in modules.get(value.value.id, set())
                and value.attr == "getattr"
            ):
                for target_name in target_names:
                    if target_name not in getattr_aliases:
                        getattr_aliases.add(target_name)
                        changed = True
    return modules, getattr_aliases


def _is_getattr_call(
    node: ast.Call,
    modules: dict[str, set[str]],
    getattr_aliases: set[str],
) -> bool:
    function = node.func
    if isinstance(function, ast.Name) and function.id in getattr_aliases:
        return True
    return (
        isinstance(function, ast.Attribute)
        and isinstance(function.value, ast.Name)
        and "builtins" in modules.get(function.value.id, set())
        and function.attr == "getattr"
    )


def _expression_module_taints(
    expression: ast.expr,
    modules: dict[str, set[str]],
) -> set[str]:
    if isinstance(expression, ast.Name):
        return modules.get(expression.id, set())
    if isinstance(expression, ast.Attribute):
        # Keep importlib taint through submodules such as importlib.util, while
        # not treating ordinary data objects such as sys.flags as sys itself.
        return _expression_module_taints(expression.value, modules) & {"importlib"}
    return set()


def _reject_restricted_syntax(tree: ast.Module, profile: str) -> None:
    modules, getattr_aliases = _bound_import_aliases(tree, profile)
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            forbidden_definition_names = (
                _DANGEROUS_GENERIC_ATTRIBUTES
                if profile == STRICT_PROFILE
                else _RUNTIME_LOADING_ATTRIBUTES
            )
            if node.name in forbidden_definition_names and not (
                profile == RUNTIME_PREFIX_PROFILE and node.name == "__getattr__"
            ):
                _fail(f"dangerous loading/reflection definition forbidden: {node.name}")
        if isinstance(node, ast.Name):
            if (
                node.id == "__builtins__"
                or node.id == "__import__"
                or (profile == STRICT_PROFILE and node.id in _DYNAMIC_BUILTIN_NAMES)
            ):
                _fail(f"dynamic execution/reflection name forbidden: {node.id}")
            if node.id in _DYNAMIC_IMPORT_NAMES:
                _fail(f"dynamic loading name forbidden: {node.id}")
            if profile == STRICT_PROFILE and node.id in _REFLECTION_HELPER_NAMES:
                _fail(f"reflection helper name forbidden: {node.id}")
            if profile == STRICT_PROFILE and node.id in getattr_aliases:
                parent = parents.get(node)
                if not (
                    isinstance(parent, ast.Call)
                    and parent.func is node
                    and _is_getattr_call(parent, modules, getattr_aliases)
                ):
                    _fail("getattr reference/alias/indirection forbidden")
        elif isinstance(node, ast.Attribute):
            forbidden_attributes = (
                _DANGEROUS_GENERIC_ATTRIBUTES
                if profile == STRICT_PROFILE
                else _RUNTIME_LOADING_ATTRIBUTES
            )
            if node.attr in forbidden_attributes:
                _fail(f"dangerous reflection/loading attribute forbidden: {node.attr}")
            if (
                node.attr in _DANGEROUS_SYS_ATTRIBUTES
                and isinstance(node.value, ast.Name)
                and "sys" in modules.get(node.value.id, set())
            ):
                _fail(f"dangerous sys import state forbidden: {node.attr}")
            if (
                (
                    node.attr == "__import__"
                    or (profile == STRICT_PROFILE and node.attr in _DYNAMIC_BUILTIN_NAMES)
                )
                and isinstance(node.value, ast.Name)
                and "builtins" in modules.get(node.value.id, set())
            ):
                _fail(f"dynamic builtin attribute forbidden: {node.attr}")
        elif isinstance(node, ast.Call) and _is_getattr_call(node, modules, getattr_aliases):
            if len(node.args) < 2:
                _fail("getattr requires a statically visible constant target name")
            target = _static_string(node.args[1])
            if target is None:
                owner_taints = _expression_module_taints(node.args[0], modules)
                if profile == STRICT_PROFILE or owner_taints & {"importlib", "sys"}:
                    _fail("nonconstant getattr target name forbidden")
                continue
            indirection_names = (
                _DANGEROUS_INDIRECTION_NAMES
                if profile == STRICT_PROFILE
                else _RUNTIME_LOADING_INDIRECTION_NAMES
            )
            if _contains_dangerous_token(target, indirection_names):
                _fail(f"dangerous getattr target forbidden: {target}")
            owner_modules = _expression_module_taints(node.args[0], modules)
            if (
                target == "__import__"
                or (profile == STRICT_PROFILE and target in _DYNAMIC_BUILTIN_NAMES)
            ) and "builtins" in owner_modules:
                _fail(f"dynamic builtin getattr target forbidden: {target}")
            if target in _DANGEROUS_SYS_ATTRIBUTES and "sys" in owner_modules:
                _fail(f"dangerous sys getattr target forbidden: {target}")
        elif isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Name) and node.value.id == "__builtins__":
                _fail("__builtins__ subscript forbidden")
            target = _static_string(node.slice)
            indirection_names = (
                _DANGEROUS_INDIRECTION_NAMES
                if profile == STRICT_PROFILE
                else _RUNTIME_LOADING_INDIRECTION_NAMES
            )
            if target is not None and (
                _contains_dangerous_token(target, indirection_names)
                or target == "__import__"
                or (profile == STRICT_PROFILE and target in _DYNAMIC_BUILTIN_NAMES)
            ):
                _fail(f"dangerous reflection/loading subscript forbidden: {target}")


def _resolve_imports_with_usage(
    source_bytes: bytes,
    module_name: str,
    declared_names: object,
    package_names: object,
    package_member_kinds: object,
    profile: str,
    *,
    is_package: bool,
) -> tuple[frozenset[str], frozenset[str]]:

    if type(source_bytes) is not bytes:
        _fail("source_bytes: immutable bytes required")
    if len(source_bytes) > MAX_SOURCE_BYTES:
        _fail("source byte cap exceeded")
    module_name = _name(module_name, "module_name")
    declared = _name_set(declared_names, "declared_names")
    packages = _name_set(package_names, "package_names")
    classifications = _package_member_classifications(package_member_kinds)
    if not packages.issubset(declared):
        _fail("package_names must be a subset of declared_names")
    if type(profile) is not str or profile not in _PROFILES:
        _fail("profile: unsupported static import profile")
    if type(is_package) is not bool:
        _fail("is_package: exact boolean required")
    try:
        tree = ast.parse(source_bytes.decode("utf-8"), filename=module_name)
        _reject_restricted_syntax(tree, profile)
    except (SyntaxError, UnicodeError, ValueError, RecursionError, MemoryError) as error:
        _fail(
            f"{module_name}: source parser/scanner rejected pathological input: "
            f"{type(error).__name__}"
        )

    imports: set[str] = set()
    used_classifications: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported = _name(alias.name, f"{module_name} import")
                imports.update(_prefixes(imported))
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module == "__future__":
                continue
            base = _name(
                _resolve_from_base(node, module_name, is_package),
                f"{module_name} from-import base",
            )
            imports.update(_prefixes(base))
            for alias in node.names:
                if alias.name == "*":
                    if (
                        profile != RUNTIME_PREFIX_PROFILE
                        or base not in declared
                        or base in packages
                    ):
                        _fail(f"{module_name}: wildcard import forbidden")
                    continue
                if base in packages:
                    member = _name(
                        f"{base}.{alias.name}",
                        f"{module_name} package-member import",
                    )
                    if profile == STRICT_PROFILE:
                        _fail(
                            f"{module_name}: package-member from-import forbidden "
                            f"in strict profile: {member}"
                        )
                    kind = classifications.get(member)
                    if kind is None:
                        _fail(f"{module_name}: package-member classification missing: {member}")
                    used_classifications.add(member)
                    if kind == "module":
                        if member not in declared:
                            _fail(
                                f"{module_name}: classified package submodule lacks "
                                f"declaration: {member}"
                            )
                        imports.update(_prefixes(member))
                    elif member in declared:
                        _fail(f"{module_name}: package-member attribute/module collision: {member}")
    return frozenset(imports), frozenset(used_classifications)


def resolve_imports(
    source_bytes: bytes,
    module_name: str,
    declared_names: object,
    package_names: object,
    package_member_kinds: object,
    profile: str,
    *,
    is_package: bool,
) -> frozenset[str]:
    """Resolve syntactic imports in immutable caller-supplied bytes.

    Runtime package-member aliases require an exact independently supplied
    ``module``/``attribute`` classification.  Strict sources reject every
    package-member from-import.  Runtime wildcard imports are permitted only
    from a declared non-package module, covering wrappers such as
    ``from .gmpy2 import *``.
    """

    imports, used = _resolve_imports_with_usage(
        source_bytes,
        module_name,
        declared_names,
        package_names,
        package_member_kinds,
        profile,
        is_package=is_package,
    )
    classifications = _package_member_classifications(package_member_kinds)
    extras = set(classifications) - set(used)
    if extras:
        _fail(f"unused package-member classifications: {sorted(extras)}")
    return imports


def _parse_records(
    value: object,
    source_bytes_by_path: object,
    package_names: frozenset[str],
    report_root: str,
) -> tuple[dict[str, ClosureRecord], dict[str, bytes]]:
    if type(value) is not list or not value:
        _fail("records: nonempty array required")
    if type(source_bytes_by_path) is not dict:
        _fail("source_bytes_by_path: exact path-to-bytes object required")
    supplied: dict[str, bytes] = {}
    for raw_path, raw in source_bytes_by_path.items():
        path = _canonical_absolute_path(raw_path, "source byte key")
        if type(raw) is not bytes:
            _fail(f"{path}: immutable bytes required")
        if len(raw) > MAX_FILE_BYTES:
            _fail(f"{path}: file byte cap exceeded")
        supplied[path] = raw

    records: dict[str, ClosureRecord] = {}
    path_owners: dict[str, str] = {}
    file_paths: set[str] = set()
    for index, item in enumerate(value):
        if type(item) is not dict or set(item) != _RECORD_KEYS:
            _fail(f"records[{index}]: exact record schema required")
        import_name = _name(item["import_name"], f"records[{index}].import_name")
        origin = item["origin_kind"]
        if type(origin) is not str or origin not in _ORIGINS:
            _fail(f"records[{index}].origin_kind: unsupported origin")
        if import_name in records:
            _fail(f"records[{index}]: duplicate import name")
        raw_path = item["path"]
        raw_sha = item["sha256"]
        if origin in {ORIGIN_BUILTIN, ORIGIN_FROZEN}:
            if raw_path is not None or raw_sha is not None:
                _fail(f"records[{index}]: builtin/frozen path and SHA must be null")
            path = None
            sha256 = None
        else:
            path = _canonical_absolute_path(raw_path, f"records[{index}].path")
            if type(raw_sha) is not str or _SHA_RE.fullmatch(raw_sha) is None:
                _fail(f"records[{index}].sha256: lowercase SHA-256 required")
            sha256 = raw_sha
            if path not in supplied:
                _fail(f"records[{index}]: no caller-supplied bytes for path")
            if hashlib.sha256(supplied[path]).hexdigest() != sha256:
                _fail(f"records[{index}]: supplied-byte SHA-256 mismatch")
            file_paths.add(path)
            owner = path_owners.get(path)
            if owner is not None and owner != import_name:
                _fail("one canonical path is mapped to multiple import names")
            path_owners[path] = import_name
            leaf = import_name.rsplit(".", 1)[-1]
            pure = pathlib.PurePosixPath(path)
            is_python_source = pure.name.endswith(".py")
            is_native_extension = pure.name.endswith(".so")
            if origin == ORIGIN_REPORT_LOCAL and not is_python_source:
                _fail(f"records[{index}]: report-local file must be .py source")
            if origin == ORIGIN_RUNTIME_PREFIX and not (is_python_source or is_native_extension):
                _fail(f"records[{index}]: runtime-prefix file must be .py or opaque .so")
            if origin == ORIGIN_NATIVE and not is_native_extension:
                _fail(f"records[{index}]: numerical native extension must be .so")
            path_leaf = (
                pure.parent.name if pure.name == "__init__.py" else pure.name.split(".", 1)[0]
            )
            if path_leaf != leaf:
                _fail(f"records[{index}]: import/path identity mismatch for {import_name}")
            within_report = _lexically_within(path, report_root)
            if origin == ORIGIN_REPORT_LOCAL and not within_report:
                _fail(f"records[{index}]: report-local path outside report root")
            if origin in {ORIGIN_RUNTIME_PREFIX, ORIGIN_NATIVE} and within_report:
                _fail(f"records[{index}]: runtime/native path reclassified inside report root")
        records[import_name] = ClosureRecord(import_name, origin, path, sha256)

    if set(supplied) != file_paths:
        _fail("caller-supplied byte keys must exactly equal file-record paths")
    declared = set(records)
    for import_name in declared:
        missing = _prefixes(import_name) - declared
        if missing:
            _fail(f"{import_name}: dotted parent prefixes lack declared records: {sorted(missing)}")
        if "." in import_name:
            parents = _prefixes(import_name) - {import_name}
            if not parents.issubset(package_names):
                _fail(f"{import_name}: dotted parents must be declared packages")
    for package_name in package_names:
        record = records.get(package_name)
        if record is None:
            _fail(f"package name lacks declared record: {package_name}")
        if record.path is not None and record.origin_kind != ORIGIN_NATIVE:
            is_init = pathlib.PurePosixPath(record.path).name == "__init__.py"
            if not is_init:
                _fail(f"file-backed package is not an __init__.py: {package_name}")
    for import_name, record in records.items():
        if record.path is None or record.origin_kind == ORIGIN_NATIVE:
            continue
        is_init = pathlib.PurePosixPath(record.path).name == "__init__.py"
        if is_init != (import_name in package_names):
            _fail(f"file-backed package declaration/path mismatch: {import_name}")
    return records, supplied


def resolve_closure(
    records: object,
    root_import_names: object,
    source_bytes_by_path: object,
    package_names: object,
    package_member_kinds: object,
    *,
    report_root: str,
) -> tuple[ClosureRecord, ...]:
    """Return the least root-reachable SHA-joined static closure.

    The caller authenticates real file identity and origins.  This function
    authenticates only the supplied bytes against record SHA-256 values and
    checks lexical report-root classification.  Package-member classifications
    must exactly cover their syntactic uses across the declared sources.
    """

    root = _canonical_absolute_path(report_root, "report_root")
    packages = _name_set(package_names, "package_names")
    classifications = _package_member_classifications(package_member_kinds)
    by_name, supplied = _parse_records(
        records,
        source_bytes_by_path,
        packages,
        root,
    )
    if type(root_import_names) is not list or not root_import_names:
        _fail("root_import_names: nonempty array required")
    roots = [_name(item, "root_import_names item") for item in root_import_names]
    if len(roots) != len(set(roots)):
        _fail("root_import_names: duplicate root")
    declared = frozenset(by_name)
    graph: dict[str, frozenset[str]] = {}
    used_classifications: set[str] = set()
    for import_name, record in by_name.items():
        parents = _prefixes(import_name) - {import_name}
        is_runtime_extension = (
            record.origin_kind == ORIGIN_RUNTIME_PREFIX
            and record.path is not None
            and pathlib.PurePosixPath(record.path).name.endswith(".so")
        )
        if (
            record.origin_kind
            in {
                ORIGIN_BUILTIN,
                ORIGIN_FROZEN,
                ORIGIN_NATIVE,
            }
            or is_runtime_extension
        ):
            graph[import_name] = frozenset(parents)
            continue
        assert record.path is not None
        profile = (
            STRICT_PROFILE if record.origin_kind == ORIGIN_REPORT_LOCAL else RUNTIME_PREFIX_PROFILE
        )
        nested_imports, nested_classifications = _resolve_imports_with_usage(
            supplied[record.path],
            import_name,
            declared,
            packages,
            classifications,
            profile,
            is_package=import_name in packages,
        )
        graph[import_name] = frozenset(parents | nested_imports)
        used_classifications.update(nested_classifications)

    extras = set(classifications) - used_classifications
    if extras:
        _fail(f"unused package-member classifications: {sorted(extras)}")

    reachable: set[str] = set()
    pending = sorted(
        {prefix for root_name in roots for prefix in _prefixes(root_name)},
        reverse=True,
    )
    while pending:
        import_name = pending.pop()
        if import_name in reachable:
            continue
        if import_name not in by_name:
            _fail(f"reachable import lacks a declared record: {import_name}")
        reachable.add(import_name)
        missing = graph[import_name] - declared
        if missing:
            _fail(f"{import_name}: reachable imports lack declared records: {sorted(missing)}")
        pending.extend(sorted(graph[import_name] - reachable, reverse=True))
    if reachable != declared:
        _fail(f"unreachable declared records: {sorted(declared - reachable)}")
    return tuple(by_name[name] for name in sorted(reachable))
