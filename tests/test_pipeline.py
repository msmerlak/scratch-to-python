"""Tests for unpack -> parse -> IR."""

from scratch2py.ir import Literal, Statement, build_scripts
from scratch2py.parser import parse_project
from scratch2py.unpack import unpack

from ._fixtures import smoke_project_json, write_smoke_sb3


def test_unpack(tmp_path):
    sb3 = write_smoke_sb3(tmp_path / "smoke.sb3")
    unpacked = unpack(sb3)
    assert "targets" in unpacked.project_json
    assert "c1.svg" in unpacked.assets
    assert "bd1.svg" in unpacked.assets


def test_parser_orders_stage_first():
    project = parse_project(smoke_project_json())
    assert project.targets[0].is_stage
    assert project.stage is not None
    assert [s.name for s in project.sprites] == ["Cat"]


def test_parser_variables_and_lists():
    project = parse_project(smoke_project_json())
    cat = project.sprites[0]
    assert any(v.name == "steps" for v in cat.variables.values())
    assert any(lst.name == "trail" for lst in cat.lists.values())


def test_ir_builds_flag_script():
    project = parse_project(smoke_project_json())
    cat = project.sprites[0]
    scripts = build_scripts(cat)
    assert len(scripts) == 1
    script = scripts[0]
    assert script.hat_opcode == "event_whenflagclicked"
    # gotoxy, repeat, say
    assert [s.opcode for s in script.body] == [
        "motion_gotoxy",
        "control_repeat",
        "looks_say",
    ]


def test_ir_resolves_repeat_substack():
    project = parse_project(smoke_project_json())
    cat = project.sprites[0]
    repeat = build_scripts(cat)[0].body[1]
    assert isinstance(repeat, Statement)
    assert repeat.opcode == "control_repeat"
    assert len(repeat.substacks) == 1
    body_opcodes = [s.opcode for s in repeat.substacks[0]]
    assert body_opcodes == ["motion_movesteps", "data_changevariableby"]


def test_ir_resolves_number_literal_input():
    project = parse_project(smoke_project_json())
    cat = project.sprites[0]
    move = build_scripts(cat)[0].body[1].substacks[0][0]
    steps = move.inputs["STEPS"]
    assert isinstance(steps, Literal)
    assert steps.is_number
    assert steps.value == "10"
