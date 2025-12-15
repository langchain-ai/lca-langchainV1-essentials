# env_utils.py
import os
import sys
import shutil
from pathlib import Path
from dotenv import dotenv_values, load_dotenv

def summarize_value(value: str) -> str:
    """Return masked form: ****last4 or boolean string."""
    lower = value.lower()
    if lower in ("true", "false"):
        return lower
    return "****" + value[-4:] if len(value) > 4 else "****" + value

def doublecheck_env(file_path: str):
    """Check environment variables against an example env file and print summaries.

    Args:
        file_path: Path to the example.env file to check against
    """
    if not os.path.exists(file_path):
        print(f"Did not find file {file_path}.")
        print("This is used to double check the key settings for the notebook.")
        print("This is just a check and is not required.\n")
        return

    # Parse the example file to identify required keys and their example values
    required_keys = {}
    with open(file_path, 'r') as f:
        lines = f.readlines()
        is_required_section = False
        for line in lines:
            stripped = line.strip()
            # Check if this is a comment line
            if stripped.startswith('#'):
                # Check if comment contains "required" (case-insensitive)
                if 'required' in stripped.lower():
                    is_required_section = True
                else:
                    # A different comment section starts
                    is_required_section = False
            # Check if this is a key=value line
            elif '=' in stripped and not stripped.startswith('#'):
                key = stripped.split('=')[0].strip()
                value = stripped.split('=', 1)[1].strip()
                if is_required_section:
                    required_keys[key] = value

    # Parse the example file to get all keys
    parsed = dotenv_values(file_path)
    issues = []

    for key in parsed.keys():
        current = os.getenv(key)
        if current is not None:
            print(f"{key}={summarize_value(current)}")

            # Check if this required key still has the example/placeholder value
            if key in required_keys:
                example_val = required_keys[key]
                if current == example_val:
                    issues.append(f"  ⚠️  {key} still has the example/placeholder value")
        else:
            print(f"{key}=<not set>")
            if key in required_keys:
                issues.append(f"  ⚠️  {key} is required but not set")

    # Print any issues found
    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(issue)
    print()


def check_venv(expected_venv_path: str = ".venv"):
    """Check if virtual environment is properly activated.

    Args:
        expected_venv_path: Expected path to the virtual environment (default: ".venv")
    """
    issues = []

    # Check sys.prefix - this is set to the venv path when activated
    current_prefix = Path(sys.prefix).resolve()
    expected_path_obj = Path(expected_venv_path).resolve()

    # Check if running in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

    if not in_venv:
        issues.append("⚠️  Virtual environment is not activated")
        issues.append("   Run: source .venv/bin/activate  (or .venv\\Scripts\\activate on Windows)")
    else:
        # Virtual env is activated, check if it's the expected one
        if current_prefix != expected_path_obj:
            issues.append(f"⚠️  Activated venv ({current_prefix}) doesn't match expected path ({expected_path_obj})")

    # Check if uv is available
    uv_available = shutil.which("uv") is not None

    if not uv_available:
        issues.append("ℹ️  'uv' command not found - this project recommends using uv for package management")
        issues.append("   Install uv: https://docs.astral.sh/uv/")

    # Print results
    if issues:
        print("Virtual Environment Check:")
        for issue in issues:
            print(issue)
        print()
    else:
        print("✅ Virtual environment is properly activated")
        if uv_available:
            print("✅ uv is available")
        print()


# ========== utility to check packages and python based on pyproject.toml  =====================================

# Requires: pip install packaging
import sys, tomllib
from pathlib import Path
from importlib import metadata
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version

def _fmt_row(cols, widths):
    return " | ".join(str(c).ljust(w) for c, w in zip(cols, widths))

def doublecheck_pkgs(pyproject_path="pyproject.toml", verbose=False):
    p = Path(pyproject_path)
    if not p.exists():
        print(f"ERROR: {pyproject_path} not found.")
        return None

    # Load pyproject + python requirement
    with p.open("rb") as f:
        data = tomllib.load(f)
    project = data.get("project", {})
    python_spec_str = project.get("requires-python") or ">=3.11"

    py_ver = Version(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    py_ok = py_ver in SpecifierSet(python_spec_str)

    # Load deps (PEP 621)
    deps = project.get("dependencies", [])
    if not deps:
        if verbose or not py_ok:
            print("No [project].dependencies found in pyproject.toml.")
            print(f"Python {py_ver} {'satisfies' if py_ok else 'DOES NOT satisfy'} requires-python: {python_spec_str}")
            print(f"Executable: {sys.executable}")
        return None

    # Evaluate deps
    results = []
    problems = []
    for dep in deps:
        try:
            req = Requirement(dep)
            name = req.name
            spec = str(req.specifier) if req.specifier else "(any)"
        except Exception:
            name, spec = dep, "(unparsed)"

        rec = {"package": name, "required": spec, "installed": "-", "path": "-", "status": "❌ Missing"}

        try:
            installed_ver = metadata.version(name)
            rec["installed"] = installed_ver
            try:
                dist = metadata.distribution(name)
                rec["path"] = str(dist.locate_file(""))
            except Exception:
                rec["path"] = "(unknown)"

            if spec not in ("(any)", "(unparsed)") and any(op in spec for op in "<>="):
                sset = SpecifierSet(spec)
                if Version(installed_ver) in sset:
                    rec["status"] = "✅ OK"
                else:
                    rec["status"] = "⚠️ Version mismatch"
            else:
                rec["status"] = "✅ OK"

        except metadata.PackageNotFoundError:
            # keep defaults: installed "-", status "❌ Missing"
            pass

        results.append(rec)
        if rec["status"] != "✅ OK":
            problems.append(rec)

    should_print = verbose or (not py_ok) or bool(problems)
    if should_print:
        # Python status
        print(f"Python {py_ver} {'satisfies' if py_ok else 'DOES NOT satisfy'} requires-python: {python_spec_str}")

        # Table (no hints column)
        headers = ["package", "required", "installed", "status", "path"]
        def short_path(s, maxlen=80):
            s = str(s)
            return s if len(s) <= maxlen else ("…" + s[-(maxlen-1):])
        rows = [[r["package"], r["required"], r["installed"], r["status"], short_path(r["path"])] for r in results]
        widths = [max(len(h), *(len(str(row[i])) for row in rows)) for i, h in enumerate(headers)]
        print(_fmt_row(headers, widths))
        print(_fmt_row(["-"*w for w in widths], widths))
        for row in rows:
            print(_fmt_row(row, widths))

        # Summarize issues without prescribing a tool
        if problems:
            print("\nIssues detected:")
            for r in problems:
                print(f"- {r['package']}: {r['status']} (required {r['required']}, installed {r['installed']}, path {r['path']})")

        if verbose or problems or not py_ok:
            print("\nEnvironment:")
            print(f"- Executable: {sys.executable}")

    return None


if __name__ == "__main__":
    check_venv()
    load_dotenv()
    doublecheck_env("example.env")
    doublecheck_pkgs(pyproject_path="pyproject.toml", verbose=True)
