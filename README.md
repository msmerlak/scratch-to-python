# Scratch → Python (scratch2py)

Convert a [Scratch](https://scratch.mit.edu/) `.sb3` project into a **runnable,
self-contained pygame Python project**. The converter emits readable Python source
(one module per sprite), copies the project's assets, and vendors a small runtime
library so the generated project runs without installing `scratch2py`.

## Install (development)

```bash
pip install -e ".[dev]"
```

## Usage

```bash
scratch2py convert path/to/game.sb3 -o out/
cd out
pip install -r requirements.txt
python main.py
```

## How it works

```
.sb3 (zip) ──unpack──► project.json + assets
          ──parse───► project model (sprites, blocks, variables, costumes, sounds)
          ──ir──────► per-sprite script ASTs (hat blocks → handlers)
          ──codegen─► readable Python source (per sprite + main.py)
          ──emit────► out/ project: main.py, sprites/, engine/, assets/, requirements.txt
```

## Scope (MVP)

Supported block categories: motion, looks, events, control, operators, variables,
lists, basic sensing, basic sound. Unsupported opcodes are emitted as clearly-commented
no-ops plus a conversion report, so generated projects always run.

Deferred: pen, custom blocks (My Blocks), clones, and extensions
(music, text-to-speech, video sensing).

## Development

```bash
ruff check .
pytest
```
