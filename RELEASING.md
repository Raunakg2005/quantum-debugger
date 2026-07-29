# Release & versioning workflow

This project develops one version at a time, each on its own long-lived dev branch,
so releases can be scheduled and shipped independently.

## Branch-per-version model

```
main            v0.7.1  (live on PyPI)
0.8.0-dev       v0.8.0  (complete, release-ready)
0.9.0-dev       v0.9.0  (complete, release-ready)
1.0.0-dev       v1.0.0  (complete, release-ready)
1.1.0-dev       v1.1.0  (complete, release-ready)
1.2.0-dev       v1.2.0  (complete, release-ready)
1.3.0-dev       v1.3.0  (active development)
```

Each `x.y.0-dev` branch is cut from the previous one, so it inherits all prior work.
`main` holds the last *released* version only.

## Adding a feature (on the active dev branch)

Every feature follows the same loop:

1. **Prototype & verify** — build the construction in a scratchpad and check it against
   a closed form, an exact computation, or the state-vector engine. If it can't be
   verified, it is abandoned — nothing unverified is committed.
2. **Module** — write the implementation in `quantum_debugger/…`.
3. **Register** — add it to the package `__init__` (import + `__all__`).
4. **Test** — a dedicated `tests/test_<feature>.py` covering every public function and
   the verifying comparison.
5. **CHANGELOG** — a bullet under the branch's `## [Unreleased] (x.y.0.dev)` section.
6. **Docs** — a section in the relevant `docs/*.md` guide.
7. **Commit** — a plain message `x.y.0.dev: <feature>` (no attribution trailers), then
   push.

## Closing a version and opening the next

When a version's theme is complete:

1. On its dev branch, rename the changelog header `## [Unreleased] (x.y.0.dev)` →
   `## [x.y.0]` with a theme summary, and push. The branch is now release-ready.
2. `git checkout -b <next>-dev` from it.
3. Bump `__version__` in `quantum_debugger/__init__.py` to `<next>.dev0`.
4. Add a fresh `## [Unreleased] (<next>.dev)` changelog section with the new theme.
5. Refresh the README "What's New" and the footer version line.
6. Commit `<next>.dev: open the <next> development line`.

## Publishing (scheduled, manual)

Releases are **not** cut automatically — they are scheduled and triggered by the
maintainer. To publish a release-ready branch:

1. Merge the `x.y.0-dev` branch into `main` (or tag it directly).
2. Create a GitHub Release for tag `vx.y.0`.
3. The `publish.yml` workflow uploads to PyPI via **Trusted Publishing (OIDC)** — no
   token or secret is stored anywhere.

`main` is protected against force-pushes and deletion.
