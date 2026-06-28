# Instructions

This project converts [Scratch](https://scratch.mit.edu/) projects to Python code:
it takes a Scratch `.sb3` archive and **generates a runnable, self-contained
pygame Python project** (readable source, one module per sprite, vendored runtime).



## References

In the `references` folder you will find some reference code, including:
- `scratch-editor`, the source code of the Scratch language


## Build, Test & Lint

```bash
pip install -e ".[dev]"   # install with dev tooling (pytest, ruff)
pytest                    # run the test suite
ruff check .              # lint
```

Tests run headless via `tests/conftest.py` (sets `SDL_VIDEODRIVER=dummy`).

Convert a project:

```bash
scratch2py convert path/to/game.sb3 -o out/
```

## Environment

Use the `.venv`

## Architecture

Pipeline (`scratch2py/`):

```
unpack.py   .sb3 (zip) -> project.json + asset blobs
parser.py   project.json -> model.py dataclasses (Stage first, then sprites)
ir.py       block graph -> Script/Statement/expression trees (hats -> handlers)
blocks/     opcode -> codegen handlers (motion, looks, events, control,
            operators, variables, sensing, sound), registered via decorators
codegen.py  IR -> readable per-sprite Python modules + main.py
emit.py     assemble out/: sprites/, vendored engine/, assets/, requirements.txt
cli.py      `scratch2py convert` entry point
```

The **runtime** (`scratch2py/runtime/`) is copied into each generated project as
`engine/`: `engine.py` (loop, cooperative scheduler, event/broadcast dispatch),
`sprite.py`, `stage.py`, `target.py` (variable/list mixin), `values.py`
(coercion), `ops.py` (operator helpers), `assets.py` (costume/sound loading).

## Key Conventions

- **Scripts are generators.** Each script becomes a method; loops emit a trailing
  `yield` (one per iteration), waits use `yield from`. The engine steps every
  thread once per frame. Non-yielding scripts run to completion immediately.
- **Coordinates:** Scratch is 480x360, centre origin, y-up; `Stage` converts to
  pygame's top-left, y-down via `scratch_to_screen`/`screen_to_scratch`.
- **Value semantics** live only in `runtime/values.py`; generated code calls
  `to_number`/`to_string`/`to_boolean`/`equals`/etc. rather than inlining rules.
- **Unsupported opcodes** become `# TODO unsupported block: <opcode>` no-ops and
  are tallied in a `ConversionReport`, so output always runs.
- **New blocks:** add a handler in the relevant `blocks/<category>.py` using the
  `@statement(...)` / `@expression(...)` decorators; no other wiring needed.
- **Shared string helpers** (`py_string`, `safe_identifier`, etc.) live in
  `util.py` to avoid a `codegen` <-> `blocks` import cycle.

## Scope (MVP)

Supported: motion, looks, events, control, operators, variables, lists, basic
sensing/sound. Deferred: pen, custom blocks (My Blocks), clones, and extensions
(music, TTS, video sensing).
