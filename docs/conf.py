# Configuration file for the Sphinx documentation builder.
import os
import sys

# Document the in-tree package (this checkout), not any older copy that happens to be
# pip-installed in the build environment.
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
project = 'QuantumDebugger'
copyright = '2025-2026, Raunak Kumar Gupta, Supervised by Dr. Vaibhav Prakash Vasani - K.J. Somaiya School of Engineering'
author = 'Raunak Kumar Gupta'

# Single source of truth: read the version from the installed package (Read the
# Docs pip-installs the package, so this stays in sync automatically).
try:
    from quantum_debugger import __version__ as release
except Exception:
    release = '0.6.1'
version = release

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
# No custom static assets yet; keep empty to avoid a missing-path warning.
html_static_path = []

# -- Extension configuration -------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# Optional heavy integrations (framework bridges, GPU, autodiff) are not needed to render the
# API docs and may be absent or version-mismatched in the build environment. Mock them so
# autodoc can import every module for its docstrings.
autodoc_mock_imports = [
    'pennylane', 'jax', 'jaxlib', 'qiskit', 'cirq',
    'torch', 'tensorflow', 'cupy', 'sklearn', 'matplotlib',
]
# Keep going if a single object fails to import rather than aborting the whole build.
autodoc_inherit_docstrings = True

# MyST settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

# Auto-generate anchors for headings (levels 1-3) so in-page "[text](#anchor)"
# links in the guides resolve instead of warning.
myst_heading_anchors = 3
