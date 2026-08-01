# AI Development Lifecycle (AIDLC)

This project is built with an **AI Development Lifecycle** — a disciplined, repeatable loop for
adding features with an AI coding agent as a first-class contributor. It is the process that
produced the algorithm library in `quantum_debugger/algorithms/`, and it is designed around one
principle: **an AI can write a lot of plausible code quickly, so the lifecycle's job is to make
sure every piece is *verified before it counts*.**

The agent-facing contract is
[`AGENTS.md`](https://github.com/Raunakg2005/quantum-debugger/blob/main/AGENTS.md) at the
repository root; this guide is the human-readable explanation of the same lifecycle.

## Why an explicit lifecycle

AI agents are fast but confidently wrong. Unstructured "vibe coding" produces code that runs,
returns numbers, and looks right — while being subtly incorrect (a wrong sign, a swapped qubit
convention, an off-by-constant bound). The AIDLC replaces "looks right" with "checked against a
known answer" at every step, and records that check as a permanent test. The result is a
library where each feature has a verifiable claim behind it.

## The five phases

```
  Intent  ─▶  Decompose  ─▶  Implement  ─▶  Verify  ─▶  Integrate
     ▲                                         │
     └───────────────  (failed check) ─────────┘
```

### 1. Intent
State the theme for a unit of work: a coherent area of quantum computing (e.g. *quantum
thermodynamics*, *query complexity*). One theme becomes one version (`x.y.0`) targeting
**25–40 features**. Capture *why* it belongs and what "done" looks like.

### 2. Decompose
Break the theme into individual, independently **verifiable** features. A feature qualifies only
if there is a known-good reference to check it against — a closed form, an exact
diagonalization, a brute-force computation, or the state-vector engine. Anything with no
possible oracle is dropped at this stage, before code is written.

### 3. Implement
Write the module in `quantum_debugger/algorithms/`, one file per topic, opening with a
substantive docstring (theme, math, what will be verified) and a docstring on every function.
Follow the house conventions: little-endian qubits, NumPy idioms, no new hard dependencies.

### 4. Verify — the gate
Check the implementation against its reference (a REPL/script computation). This is the phase
that gives the lifecycle its value; historically it catches a real bug in most versions —
examples that were caught and fixed rather than shipped:

| Version | Bug the verify gate caught |
|---------|----------------------------|
| 2.1 | Landau-Zener used `/2v`; the two-level sweep needs `/4v` (gap = 2× coupling). |
| 2.2 | Parameter-shift Hessian had the wrong sign/denominator. |
| 2.6 | Six-state QKD threshold root-found in a clipped-zero region. |
| 2.7 | Cluster-state PEPS was missing the CZ phase (gave `|+⟩⁴`). |
| 2.8 | MBQC CNOT used the wrong control/target convention. |
| 3.0 | Grover "optimality" bound used `√N` instead of `(π/4)√N`. |

**If the check fails, fix the code — never loosen the tolerance or weaken the check to force a
pass.** If a construction turns out to be unverifiable, abandon it and commit nothing.

### 5. Integrate
Make the verification permanent and the feature discoverable:
1. Add/extend the pytest suite (`tests/test_<theme>.py`) so the check runs forever.
2. Wire exports into `algorithms/__init__.py` (`import` + `__all__`); handle name collisions.
3. Add a CHANGELOG bullet, and — for a new theme — a narrative guide page in `docs/`.
4. Commit with a plain message (`x.y.0.dev: <theme> — … (<N> features)`) and push the dev branch.

## Definition of done

A feature is done when **all** of these hold:

- [ ] Docstring states what it computes and what it is verified against.
- [ ] Verified against a closed form / exact / brute-force reference.
- [ ] A passing pytest assertion encodes that verification.
- [ ] Exported in `algorithms/__init__.py` (`import` + `__all__`).
- [ ] A CHANGELOG bullet (and a guide entry for a new theme) exists.

## Branch-per-version release cadence

Each version is developed to completion on its own `x.y.0-dev` branch, branched from the
previous version (so branches are cumulative). Releases are scheduled by the maintainer roughly
a month apart; the agent never publishes to PyPI or force-pushes without explicit approval, and
never adds AI/tool attribution to commits, PRs, or docs.

## Applying AIDLC to a new contribution

1. Pick a theme (Intent) and open/continue the `x.y.0-dev` branch.
2. List the verifiable features (Decompose).
3. For each: Implement → Verify → add test → export → CHANGELOG (Integrate).
4. When the version hits its feature target and the suite is green, it is ready for the
   maintainer's scheduled release.
