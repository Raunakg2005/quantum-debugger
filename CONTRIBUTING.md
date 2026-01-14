# Contributing to Quantum Debugger

Thank you for your interest in contributing to quantum-debugger!

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/Raunakg2005/quantum-debugger.git
cd quantum-debugger
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Install in Development Mode

```bash
pip install -e ".[dev]"
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clear, documented code
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation

### 3. Run Tests

```bash
# Run all tests
pytest tests/

# Run specific tests
pytest tests/qml/

# With coverage
pytest tests/ --cov=quantum_debugger
```

### 4. Check Code Quality

```bash
# Format code
black quantum_debugger/ tests/

# Check linting
flake8 quantum_debugger/ --max-line-length=100

# Type checking
mypy quantum_debugger/ --ignore-missing-imports
```

### 5. Commit Changes

```bash
git add .
git commit -m "Description of changes"
```

Follow commit message format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Standards

### Python Style

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use meaningful variable names

### Documentation

- Add docstrings to all public functions/classes
- Use NumPy style docstrings
- Include examples in docstrings
- Update relevant guides in `docs/`

### Testing

- Write tests for all new features
- Aim for 90%+ code coverage
- Use descriptive test names
- Test edge cases

## Pull Request Process

1. **Update documentation** - Add/update relevant docs
2. **Add tests** - Ensure 100% test coverage for new code
3. **Pass CI checks** - All tests and linting must pass
4. **Get review** - Wait for maintainer review
5. **Address feedback** - Make requested changes
6. **Merge** - Maintainer will merge when approved

## Areas for Contribution

### High Priority

- Additional quantum algorithms
- Performance optimizations
- Documentation improvements
- Bug fixes

### Medium Priority

- New examples/tutorials
- Integration with other frameworks
- Visualization tools

### Low Priority

- Code refactoring
- Test improvements
- Minor features

## Questions?

- Open an issue on [GitHub](https://github.com/Raunakg2005/quantum-debugger/issues)
- Use [Discussions](https://github.com/Raunakg2005/quantum-debugger/discussions) for questions
- Connect on [LinkedIn](https://www.linkedin.com/in/raunak-kumar-gupta-7b3503270/)
- Check the [documentation](https://github.com/Raunakg2005/quantum-debugger#readme)

## Code of Conduct

Be respectful, inclusive, and professional.

Thank you for contributing!
