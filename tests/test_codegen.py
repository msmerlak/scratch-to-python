"""Tests for codegen and end-to-end project emission/execution."""

import py_compile

from scratch2py.codegen import ConversionReport, generate_target_module
from scratch2py.ir import build_scripts
from scratch2py.parser import parse_project
from scratch2py.unpack import unpack

from ._fixtures import smoke_project_json, write_smoke_sb3


def test_generated_module_is_valid_python(tmp_path):
    project = parse_project(smoke_project_json())
    cat = project.sprites[0]
    source = generate_target_module(ConversionReport(), cat, build_scripts(cat))
    # Key fragments.
    assert "class Cat(SpriteBase):" in source
    assert "def flag_1(self):" in source
    assert "self.move(10)" in source
    assert "yield" in source
    # It must compile.
    path = tmp_path / "cat.py"
    path.write_text(source)
    compile(source, str(path), "exec")


def test_unsupported_block_is_reported():
    project = parse_project(smoke_project_json())
    cat = project.sprites[0]
    # Inject an unknown opcode.
    cat.blocks["b5"].opcode = "pen_clear"
    report = ConversionReport()
    source = generate_target_module(report, cat, build_scripts(cat))
    assert "# TODO unsupported block: pen_clear" in source
    assert "pen_clear" in report.unsupported_opcodes


def test_emit_project_and_compile_all(tmp_path):
    from scratch2py.emit import emit_project

    sb3 = write_smoke_sb3(tmp_path / "smoke.sb3")
    unpacked = unpack(sb3)
    project = parse_project(unpacked.project_json)
    out = tmp_path / "out"
    emit_project(project, unpacked, out)

    # Expected layout.
    assert (out / "main.py").exists()
    assert (out / "sprites" / "cat.py").exists()
    assert (out / "sprites" / "stage.py").exists()
    assert (out / "engine" / "engine.py").exists()
    assert (out / "assets" / "c1.svg").exists()
    assert (out / "requirements.txt").exists()

    # Every generated/vendored python file must compile.
    for py_file in out.rglob("*.py"):
        py_compile.compile(str(py_file), doraise=True)


def test_generated_project_runs_headless(tmp_path):
    import pygame

    from scratch2py.emit import emit_project

    sb3 = write_smoke_sb3(tmp_path / "smoke.sb3")
    unpacked = unpack(sb3)
    project = parse_project(unpacked.project_json)
    out = tmp_path / "out"
    emit_project(project, unpacked, out)

    # Import the generated project from its output directory.
    import sys

    sys.path.insert(0, str(out))
    try:
        pygame.init()
        pygame.display.set_mode((480, 360))
        import importlib

        engine_mod = importlib.import_module("engine")
        stage_mod = importlib.import_module("sprites.stage")
        cat_mod = importlib.import_module("sprites.cat")

        eng = engine_mod.Engine("test")
        eng.add_target(stage_mod.Stage())
        eng.add_target(cat_mod.Cat())
        cat = eng.sprites[0]
        for target in eng._all_targets():
            target.setup_scripts()
        for _sprite, method in eng._flag_hats:
            eng.spawn(method)
        for _ in range(10):
            eng._step_threads()

        # 5 repeats of "move 10" -> x == 50; "steps" incremented 5 times.
        assert cat.x == 50
        assert cat.var("steps") == 5
        assert cat._bubble == ("done", "say")
    finally:
        pygame.quit()
        sys.path.remove(str(out))
        for mod in ("engine", "sprites.stage", "sprites.cat", "sprites"):
            sys.modules.pop(mod, None)
