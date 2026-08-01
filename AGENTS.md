# AGENTS.md — working agreement for AI agents on quantum-debugger

This file is the contract an AI coding agent follows when working in this repository. It
encodes how the project is built, tested, documented, and released. Human contributors can
read it too. (See `docs/aidlc_guide.md` for the full AI Development Lifecycle.)

## What this project is

`quantum-debugger` is a pure-Python quantum simulation, algorithms, and debugging toolkit:
state-vector and Clifford/stabilizer engines, a large *verified* algorithm library
(`quantum_debugger/algorithms/`), quantum machine learning, error correction and mitigation,
tensor networks, and quantum-information/complexity theory. It has no mandatory dependency
beyond NumPy/SciPy; framework integrations (Qiskit, PennyLane, …) are optional extras.

## Golden rule: verify, never fake

**Every feature must be verified against a known-good outcome before it ships** — a closed
form, an exact diagonalization, brute force, or the state-vector engine. If a construction
cannot be verified, it is abandoned and nothing is committed. This is non-negotiable and is
what distinguishes this library. Tests encode the verification; a feature without a passing
verification is not done.

Concretely, prefer checks like:
- `assert np.allclose(result, exact_reference, atol=1e-9)`
- comparing a formula to a simulation (e.g. Landau-Zener, Jarzynski)
- comparing an encoding to brute force (e.g. QUBO ground state, Boolean-function measures)

If a check only "roughly" holds, weaken the *claim* (docstring/CHANGELOG) to match what is
actually proven — do not weaken the tolerance to force a pass.

## Repository layout

- `quantum_debugger/algorithms/` — one module per topic; each is self-contained and opens
  with a substantive module docstring (theme, math, what is verified).
- `quantum_debugger/algorithms/__init__.py` — re-exports the public API and lists it in
  `__all__`. **Every new public function must be imported here and added to `__all__`.**
- `tests/` — pytest suites, one per theme (`test_<theme>.py`).
- `docs/` — Sphinx site: per-theme narrative guides (`*_guide.md`) plus autodoc API pages.
- `CHANGELOG.md` — Keep-a-Changelog format; one `- **Name** (\`api\`) — …` bullet per feature.

## Conventions

- **Qubit ordering is little-endian**: qubit 0 is the least-significant bit; a gate on
  qubit `i` is the *last-but-`i`* Kronecker factor. Match this everywhere.
- **Style**: match the surrounding code — NumPy idioms, module docstring + per-function
  docstrings, no one-letter public names. Keep comment density like the neighbours.
- **No new hard dependencies.** Optional integrations stay behind try/except imports.
- **Name collisions**: the algorithms package is flat, so check for an existing symbol before
  exporting; if a name is taken, export from the submodule instead and note it in the
  CHANGELOG bullet (`` `submodule.name` ``).

## Build & test

```bash
pip install -e .
python -m pytest tests/ -q
```

Run a single theme suite while iterating:

```bash
python -m pytest tests/test_<theme>.py -q
```

Notes:
- On some machines `coverage`/`pytest-cov` crashes at `import numpy`; if so, run the plain
  suite (`python -m pytest`) and do not chase a local coverage percentage.
- This is a Windows-first checkout; prefer `python -m pytest` over bare `pytest`.

## Release workflow (branch per version)

Development is **one branch per version**: `x.y.0-dev`. A version is built to completion on
its own branch, then the maintainer schedules pushes/releases roughly a month apart. New
versions branch from the previous one, so each is cumulative.

Per feature, the loop is:

1. Implement the module + docstrings.
2. Verify it (script/REPL) against a closed form or exact result.
3. Add/extend the pytest suite so the verification is permanent.
4. Wire exports into `algorithms/__init__.py` (`import` + `__all__`).
5. Add a CHANGELOG bullet under the current `[Unreleased] (x.y.0.dev)` section.
6. Commit; push the dev branch.

Each version targets **25–40 genuine, verified features**.

## Commit & PR rules

- Commit messages are plain and factual, e.g.
  `x.y.0.dev: <theme> — <key modules/features> (<N> features)`.
- **Never add AI/tool attribution** to commits, PRs, code comments, docs, or release notes
  (no `Co-Authored-By`, no "Generated with …" trailers). Messages end at the last content
  line.
- Commit or push only when asked, or as part of the per-feature loop above. If on the default
  branch, branch first.
- Do irreversible/outward-facing actions (deleting data, publishing to PyPI, force-pushing)
  only with explicit approval.

## Definition of done (per feature)

- [ ] Implemented with a clear docstring stating what is computed and what it is verified against.
- [ ] Verified against a closed form / exact / brute-force reference.
- [ ] Covered by a passing pytest assertion.
- [ ] Exported in `algorithms/__init__.py` (`import` + `__all__`), collisions handled.
- [ ] Documented with a CHANGELOG bullet (and a narrative-guide entry for a new theme).
