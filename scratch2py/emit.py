"""Assemble a generated, runnable pygame project on disk.

Given a parsed :class:`~scratch2py.model.Project` and the raw asset blobs, this
writes the full output tree::

    out/
      main.py
      sprites/<name>.py        # one module per target (Stage first)
      engine/                  # vendored copy of the runtime library
      assets/                  # costume + sound files from the .sb3
      requirements.txt
      README.md
"""

from __future__ import annotations

import shutil
from pathlib import Path

from . import codegen
from .codegen import ConversionReport, safe_class_name, safe_identifier
from .ir import build_scripts
from .model import Project
from .unpack import UnpackedProject

_RUNTIME_DIR = Path(__file__).parent / "runtime"

_REQUIREMENTS = "pygame>=2.5\n# Optional: enables SVG costume rendering\n# cairosvg>=2.7\n"


def _generated_readme(title: str) -> str:
    return (
        f"# {title}\n\n"
        "This project was generated from a Scratch `.sb3` file by "
        "[scratch2py](https://github.com/).\n\n"
        "## Run\n\n"
        "```bash\n"
        "pip install -r requirements.txt\n"
        "python main.py\n"
        "```\n\n"
        "Controls and behaviour mirror the original Scratch project. Close the "
        "window to quit.\n"
    )


def emit_project(
    project: Project,
    unpacked: UnpackedProject,
    out_dir: str | Path,
) -> ConversionReport:
    out = Path(out_dir)
    sprites_dir = out / "sprites"
    engine_dir = out / "engine"
    assets_dir = out / "assets"
    for d in (out, sprites_dir, engine_dir, assets_dir):
        d.mkdir(parents=True, exist_ok=True)

    report = ConversionReport()

    # Generate one module per target, tracking (module, class, is_stage) order.
    modules: list[tuple[str, str, bool]] = []
    used_module_names: set[str] = set()
    for target in project.targets:
        module_name = _unique_module_name(target.name, used_module_names)
        class_name = safe_class_name(target.name)
        scripts = build_scripts(target)
        source = codegen.generate_target_module(report, target, scripts)
        (sprites_dir / f"{module_name}.py").write_text(source, encoding="utf-8")
        modules.append((module_name, class_name, target.is_stage))

    (sprites_dir / "__init__.py").write_text("", encoding="utf-8")

    # main.py
    (out / "main.py").write_text(codegen.generate_main(project, modules), encoding="utf-8")

    # Vendor the runtime library as engine/.
    _copy_runtime(engine_dir)

    # Assets.
    _write_assets(project, unpacked, assets_dir)

    # Project metadata files.
    (out / "requirements.txt").write_text(_REQUIREMENTS, encoding="utf-8")
    (out / "README.md").write_text(
        _generated_readme(codegen.project_title(project)), encoding="utf-8"
    )
    (out / "CONVERSION_REPORT.txt").write_text(report.summary() + "\n", encoding="utf-8")

    return report


def _unique_module_name(name: str, used: set[str]) -> str:
    base = safe_identifier(name, prefix="sprite")
    candidate = base
    i = 2
    while candidate in used:
        candidate = f"{base}_{i}"
        i += 1
    used.add(candidate)
    return candidate


def _copy_runtime(engine_dir: Path) -> None:
    for py_file in _RUNTIME_DIR.glob("*.py"):
        shutil.copy2(py_file, engine_dir / py_file.name)


def _write_assets(project: Project, unpacked: UnpackedProject, assets_dir: Path) -> None:
    wanted: set[str] = set()
    for target in project.targets:
        for costume in target.costumes:
            wanted.add(costume.md5ext)
        for sound in target.sounds:
            wanted.add(sound.md5ext)
    for md5ext in wanted:
        blob = unpacked.assets.get(md5ext)
        if blob is not None:
            (assets_dir / md5ext).write_bytes(blob)
