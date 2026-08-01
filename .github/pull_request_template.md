## Description

Brief description of changes.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Changes Made

- Change 1
- Change 2
- Change 3

## Testing

- [ ] All tests pass (`python -m pytest tests/`)
- [ ] Added new tests for new features
- [ ] Code follows style guidelines (`black`, `flake8`)
- [ ] Documentation updated

## Verification (AI Development Lifecycle)

The project's golden rule is **verify, never fake** — see [AGENTS.md](../AGENTS.md) and the
[AIDLC guide](../docs/aidlc_guide.md). For each new feature:

- [ ] Verified against a closed form / exact diagonalization / brute force / the state-vector engine
- [ ] The verification is encoded as a passing pytest assertion (not just a one-off script)
- [ ] Exported in `quantum_debugger/algorithms/__init__.py` (`import` + `__all__`), name collisions handled
- [ ] CHANGELOG bullet added (and a narrative guide entry for a new theme)

## Checklist

- [ ] Code is well-documented
- [ ] Commit messages are clear
- [ ] No breaking changes (or clearly documented)
- [ ] Ready for review

## Related Issues

Closes #(issue number)
