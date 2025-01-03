import os
import re
from collections import namedtuple
from pathlib import Path

from sphinx.application import Sphinx

AutodocPath = namedtuple('AutodocPath', ['src', 'rst', 'title'])


def generate_module_content(src: Path, module_name: str):
    '''Generate reST content per module
    '''
    content = f"\n{module_name}\n{'-' * len(module_name)}\n\n"

    # TODO: 実装する

    return content


def generate_rst_files(app: Sphinx):
    '''Create/overwrite *.rst files based on VB source directory.

    This is called just after the builder is inited.
    '''
    if not app.config.vb_autodoc:
        return

    for path_info in app.config.vb_autodoc_paths:
        autodoc_path = AutodocPath(*path_info)
        title = autodoc_path.title
        rst_content = f"{title}\n{'=' * len(title)}\n\n"

        src_dir = Path(app.confdir) / autodoc_path.src
        for vb_file in os.listdir(src_dir):
            if vb_file.endswith(('.bas', '.vb', '.vbs')):
                module_name = os.path.splitext(os.path.basename(vb_file))[0]
                src_file = src_dir / vb_file
                rst_content += generate_module_content(src_file, module_name)

        dest_file = Path(app.srcdir) / (autodoc_path.rst + '.rst')
        with open(dest_file, 'w', encoding='utf-8') as f:
            f.write(rst_content)


def setup(app: Sphinx):
    '''Set up vb_autodoc feature.
    '''
    # Config parameter to enable autodoc.
    # > sphinx-build html docs/source docs/build -D vb_autodoc=1
    app.add_config_value('vb_autodoc', False, 'env', bool)

    # Config parameter to set source dirs, rst names, and titles.
    # e.g. [('../../macros', 'modules', 'Modules')]
    #    makes 'modules.rst' from '../../macros/*.bas' files.
    # '../../macros' should be relative from Sphinx conf dir.
    # 'modules' is treated as 'modules.rst' relative from Sphinx src dir.
    # 'Modules' will be the title of 'modules.rst' page.
    app.add_config_value('vb_autodoc_paths', [], 'env', list[AutodocPath])

    # Add process just after the builder is inited.
    app.connect('builder-inited', generate_rst_files)
