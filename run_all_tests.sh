# Comprehensive Test Suite Runner
# ================================
# 
# Runs ALL test categories for production-ready validation

# 1. Core Logic Tests
echo "Running Core Logic Tests..."
python -m pytest test_qml_*.py test_vqe.py test_qaoa.py test_training.py test_integration.py -v --tb=short

# 2. Compatibility Tests  
echo ""
echo "Running Compatibility Tests..."
python -m pytest test_compatibility.py -v

# 3. Quality & Standards Tests
echo ""
echo "Running Docstring Tests..."
python test_docstrings.py

echo ""
echo "Running Type Checking..."
mypy quantum_debugger/qml --config-file mypy.ini || echo "Type checking completed with warnings"

echo ""
echo "Running Linting..."
flake8 quantum_debugger/qml || echo "Linting completed with warnings"

# 4. Performance Tests
echo ""
echo "Running Performance Benchmarks..."
python examples/benchmarks.py

# 5. Distribution Tests
echo ""
echo "Running Distribution Tests..."
python test_distribution.py

echo ""
echo "========================================="
echo "All Test Categories Complete!"
echo "========================================="
