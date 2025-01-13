import os
import re
import xml.etree.ElementTree as ET
from collections import namedtuple
from io import StringIO
from pathlib import Path
from typing import Iterator

from sphinx.application import Sphinx

# For config 'vb_autodoc_paths'. See `setup()` below.
AutodocPath = namedtuple('AutodocPath', ['src', 'rst', 'title'])


def xml_to_dict(xml_string) -> dict[str, str]:
    '''Convert document comment (xml) to dict.
    '''
    root = ET.fromstring(f'<root>{xml_string}</root>')
    result = {}
    for child in root:
        if child.tag == 'remarks' and 'remarks' in result:
            result['remarks'] += '\n' + child.text
        else:
            name = child.get('name', '')
            if name:
                result[f'{child.tag} {name}'] = child.text
            else:
                result[child.tag] = child.text
    return result


class DocComment:
    '''Object containing doc comment (xml) and/or func signature.
    '''
    def __init__(self, xml: str, sig: str):
        self.xml = xml
        self.sig = sig

    def get_param_type(self, param_name: str):
        '''Get paramter type from 'param As xx' part of signature.
        '''
        re_ptn = re.compile(param_name + r'\s+As\s+(\w+)')
        match = re_ptn.search(self.sig)
        if match and match.lastindex > 0:
            return match.group(1)
        else:
            return ''

    def get_return_type(self):
        '''Get return type from 'As xx' at end of signature.
        '''
        re_ptn = re.compile(r'As\s+(\w+)\s*$')
        match = re_ptn.search(self.sig)
        if match and match.lastindex > 0:
            return match.group(1)
        else:
            return ''

    def to_function_directive(self, module_name: str) -> str:
        indent = '   '
        content = f'.. vb:function:: {self.sig}\n'

        if module_name:
            content += f'{indent}:module: {module_name}\n'

        content += '\n'

        if not self.xml:
            return content

        xml_data = xml_to_dict(self.xml)

        if 'summary' in xml_data:
            summary_lines = xml_data['summary'].strip().split('\n')
            for line in summary_lines:
                content += f'{indent}{line.strip()}\n'
            content += '\n'

        content_length = len(content)

        for key in xml_data:
            if key.split()[0] in ('param', 'parameter', 'arg', 'argument'):
                param_name = key.split()[1]
                content += f'{indent}:{key}: {xml_data[key]}\n'

                param_type = self.get_param_type(param_name)
                if param_type:
                    content += f'{indent}:type {param_name}: {param_type}\n'
                continue

            if key in ('returns', 'return'):
                content += f'{indent}:{key}: {xml_data[key]}\n'
                return_type = self.get_return_type()
                if return_type:
                    content += f'{indent}:rtype: {return_type}\n'
                continue

            if key == 'rtype':
                content += f'{indent}:{key}: {xml_data[key]}\n'
                continue

        has_field_list = len(content) > content_length
        if has_field_list:
            content += '\n'

        if 'remarks' in xml_data:
            remark_lines = xml_data['remarks'].strip().split('\n')
            for line in remark_lines:
                content += f'{indent}{line}\n'
            content += '\n'

        return content

    def to_module_desc(self) -> str:
        content = ''
        xml_data = xml_to_dict(self.xml)

        if 'summary' in xml_data:
            summary_lines = xml_data['summary'].strip().split('\n')
            for line in summary_lines:
                content += f'{line}\n'
            content += '\n'

        if 'remarks' in xml_data:
            remark_lines = xml_data['remarks'].strip().split('\n')
            for line in remark_lines:
                content += f'{line}\n'
            content += '\n'

        return content

    def to_rest(self, module_name: str) -> str:
        if self.sig:
            return self.to_function_directive(module_name)
        else:
            return self.to_module_desc()


def extract_doccomments(f: StringIO) -> Iterator[DocComment]:
    '''Generator of Document Comments from a text stream
    '''
    # Regex pattern for function signature.
    sig_ptn = re.compile(
        r'((Public|Private|Friend|Protected)\s+)?(Function|Sub)\s+.+')

    xml = ''
    eof = False

    while not eof:
        line = f.readline()
        if not line:
            eof = True
        line = line.strip()

        # Extract document comment (maybe empty) and function signature.
        if sig_ptn.match(line):
            yield DocComment(xml, line)
            xml = ''
            continue

        # Keep part of document comment in xml.
        if line.startswith("'''"):
            if xml:
                xml += '\n'
            xml += line[3:].strip()
            continue

        # Neither function signature nor xml: yield document comment if kept.
        if xml:
            yield DocComment(xml, '')
            xml = ''


def generate_module_content(src_file: Path, module_name: str) -> str:
    '''Generate reST content per module

    Parameters
    ----------
    src_file : Path
        Path to VB module source file.
    module_name : str
        Module name to show in document.

    Returns
    -------
    module_content : str
        Document content in reStructuredText for the module.
    '''
    # Module headline (level2)
    byte_length = len(module_name.encode('utf-8'))
    content = f"\n{module_name}\n{'-' * byte_length}\n\n"

    with open(src_file, 'r', encoding='utf-8') as f:
        for doccomment in extract_doccomments(f):
            content += doccomment.to_rest(module_name)

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
