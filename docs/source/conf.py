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
    # 'sphinx.ext.autosectionlabel',  # 自動でセクションラベルを付与する
    'sphinx_vb_domain',
]

templates_path = ['_templates']
exclude_patterns = []

language = 'ja'

# autosectionlabel_prefix_document = True  # セクションラベルにファイル名を付ける

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

# vb_add_function_labels = False  # 関数のラベルを生成しない
# vb_encode_invalid_labels = False  # 無効なラベルをエンコードしない
# vb_add_docname_to_labels = True  # ラベルにファイル名を付ける
# vb_docname_label_delimiter = '__'  # ラベルのファイル名の区切り文字
# vb_autodoc_module_labels = True  # Autodoc でモジュールのラベルを生成する
