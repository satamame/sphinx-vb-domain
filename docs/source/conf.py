# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from textwrap import dedent

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'vb_domain'
copyright = '2024, satamame.com'
author = 'satamame.com'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    # 'sphinx.ext.autosectionlabel',
    'sphinx_vb_domain',
]

templates_path = ['_templates']
exclude_patterns = []

language = 'ja'

# autosectionlabel_prefix_document = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Options for MyST-Parser -------------------------------------------------
myst_enable_extensions = [
    'fieldlist',
]
myst_heading_anchors = 3

# -- Options for sphinx_vb_domain --------------------------------------------

module_notes = {
    '__page__': '補足\n----\n\nページの補足説明',
    'Module1': '補足\n~~~~\n\nモジュールの補足説明',
    'Module1.procedureWithoutDocComment': dedent('''
        補足
        ^^^^

        - 関数の補足説明1
        - 関数の補足説明2
    '''),
}

vb_autodoc_paths = [
    ('../../macros/001', 'modules', 'モジュール', module_notes),
]

# vb_add_function_labels = False
vb_add_docname_to_labels = True
