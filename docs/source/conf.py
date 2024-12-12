# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

from sphinx_vb_domain.vb_domain import VBDomain

# -- Path setup --------------------------------------------------------------

sys.path.insert(0, os.path.abspath('../../macros'))  # 何のため？


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'vb_domain'
copyright = '2024, satamame.com'
author = 'satamame.com'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx_vb_domain',
]

templates_path = ['_templates']
exclude_patterns = []

language = 'ja'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Options for MyST-Parser -------------------------------------------------
myst_enable_extensions = [
    'fieldlist',
]


# -- Custom Setup ------------------------------------------------------------
def setup(app):
    app.add_domain(VBDomain)
