# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = 'QuantumDebugger'
copyright = '2025, Raunak Kumar Gupta - K.J. Somaiya School of Engineering'
author = 'Raunak Kumar Gupta'
release = '0.4.1'

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
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# MyST settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
