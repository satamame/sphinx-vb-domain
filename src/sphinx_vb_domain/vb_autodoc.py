import os
import re
import xml.etree.ElementTree as ET
from collections import namedtuple
from io import StringIO
from pathlib import Path
from typing import Iterator
from unicodedata import east_asian_width

from sphinx.application import Sphinx

# For config 'vb_autodoc_paths'. See `setup()` below.
AutodocPath = namedtuple('AutodocPath', ['src', 'rst', 'title', 'notes'])

# Regex pattern for function signature.
sig_ptn = re.compile(
    r'((Public|Private|Friend|Protected)\s+)?(Function|Sub)\s+([^\(\s]+)')


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

    @property
    def func_name(self) -> str:
        '''Extract the function name from the signature.'''
        if not self.sig:
            return ''
        match = sig_ptn.match(self.sig)
        if match:
            return match.group(4)  # Return the function name
        return ''


def extract_doccomments(f: StringIO) -> Iterator[DocComment]:
    '''Generator of Document Comments from a text stream
    '''
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


def headline_len(title: str) -> int:
    def char_width(char: str) -> int:
        return 2 if east_asian_width(char) in ('F', 'W') else 1

    return sum(char_width(char) for char in title)


def sanitize_note(note: str) -> str:
    '''Remove or demote headings in the note content.'''
    # Replace reST heading patterns with plain text
    sanitized_note = re.sub(
        r'^(.*)\n[-=~^`]+\n', r'**\1**\n', note, flags=re.MULTILINE)
    return sanitized_note


def generate_module_content(
        src_file: Path, module_name: str, notes: dict) -> str:
    '''Generate reST content per module

    Parameters
    ----------
    src_file : Path
        Path to VB module source file.
    module_name : str
        Module name to show in document.
    notes : dict
        Dict to map notes to targets where to add.

    Returns
    -------
    module_content : str
        Document content in reStructuredText for the module.
    '''
    # Module headline (level2)
    content = f"\n{module_name}\n{'-' * headline_len(module_name)}\n\n"

    # Add note to module block using notes.
    module_note = notes.get(module_name)
    if module_note:
        content += f"{sanitize_note(module_note)}\n\n"

    with open(src_file, 'r', encoding='utf-8') as f:
        for doccomment in extract_doccomments(f):
            content += doccomment.to_rest(module_name)
            func_note = notes.get(f'{module_name}.{doccomment.func_name}')
            if func_note:
                content += f"{sanitize_note(func_note)}\n\n"

    return content


def generate_rst_files(app: Sphinx):
    '''Create/overwrite *.rst files based on VB source directory.

    This is called just after the builder is inited.
    '''
    if not app.config.vb_autodoc:
        return

    for path_info in app.config.vb_autodoc_paths:
        if len(path_info) < 3:
            raise ValueError('vb_autodoc_paths must have at least 3 elements.')
        if len(path_info) < 4:
            path_info = (*path_info, {})

        autodoc_path = AutodocPath(*path_info)
        title = autodoc_path.title
        rst_content = f"{title}\n{'=' * headline_len(title)}\n\n"

        # Add note to rst_content using notes.
        page_note = autodoc_path.notes.get('__page__')
        if page_note:
            rst_content += f"{sanitize_note(page_note)}\n\n"

        src_dir = Path(app.confdir) / autodoc_path.src
        for vb_file in os.listdir(src_dir):
            if vb_file.endswith(('.bas', '.vb', '.vbs')):
                module_name = os.path.splitext(os.path.basename(vb_file))[0]
                src_file = src_dir / vb_file
                rst_content += generate_module_content(
                    src_file, module_name, autodoc_path.notes)

        dest_file = Path(app.srcdir) / (autodoc_path.rst + '.rst')
        with open(dest_file, 'w', encoding='utf-8') as f:
            f.write(rst_content)


def setup(app: Sphinx):
    '''Set up vb_autodoc feature.
    '''
    # Config parameter to enable autodoc.
    # > sphinx-build html docs/source docs/build -D vb_autodoc=1
    app.add_config_value('vb_autodoc', False, 'env', bool)

    # Config parameter to set source dirs, rst names, titles, and callback.
    # e.g. [('../../macros', 'modules', 'Modules', notes)]
    #    makes 'modules.rst' from '../../macros/*.bas' files.
    # '../../macros' should be relative from Sphinx conf dir.
    # 'modules' is treated as 'modules.rst' relative from Sphinx src dir.
    # 'Modules' will be the title of 'modules.rst' page.
    # notes is a callback function to add note, or None if not needed.
    app.add_config_value('vb_autodoc_paths', [], 'env', list[AutodocPath])

    # Add process just after the builder is inited.
    app.connect('builder-inited', generate_rst_files)
