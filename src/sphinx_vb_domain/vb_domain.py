import re

from docutils import nodes
from docutils.nodes import Element
from docutils.parsers.rst import directives, Directive
from sphinx import addnodes
from sphinx.addnodes import pending_xref, desc_signature
from sphinx.builders import Builder
from sphinx.directives import ObjectDescription, ObjDescT
from sphinx.domains import Domain
from sphinx.environment import BuildEnvironment
from sphinx.roles import XRefRole


class VBXRefRole(XRefRole):
    '''For VBDomain's cross-reference e.g. func role (vb:func).
    '''
    # Visual Basic 固有のリンク処理が必要な場合は process_link() を
    # オーバーライドする。
    pass


class VBFunction(ObjectDescription):
    '''For function directive (vb:function).
    '''
    # Class variables are function directive's specs.
    has_content = True  # for function summary or details.
    required_arguments = 1  # 1 arg is enough as whole declaration.
    option_spec = {
        'module': directives.unchanged,
        'param': directives.unchanged,
        'type': directives.unchanged,
        'returns': directives.unchanged,
    }

    def handle_signature(
            self, sig: str, signode: desc_signature) -> ObjDescT:
        '''Parse the function signature and add nodes to the signode.

        This function will be called from autodoc.

        Parameters
        ----------
        sig : str
            Function declaration from VB source code.
        signode : desc_signature
            Node for signature structure.

        Returns
        -------
        ObjDescT
            Object identifier.
        '''
        # Split signature into 3 parts
        match = re.match(r'^(.*?)\s*(\(.*?\))?\s*(As\s+.+)?$', sig)
        if not match:
            raise ValueError(f"Invalid signature: {sig}")

        # Part 1: access modifier and function name
        access_and_name = match.group(1).strip()
        # Part 2: parameters (without ())
        parameters = match.group(2).strip("()") if match.group(2) else ""
        args = [arg.strip() for arg in parameters.split(',')]
        # Part 3: return type
        return_type = match.group(3).removeprefix("As").strip() \
            if match.group(3) else ""

        # Extract access modifier
        valid_modifiers = [
            'Public', 'Private', 'Protected', 'Friend', 'Protected Friend',
            'Private Protected']

        parts = access_and_name.split()

        if len(parts) >= 2 and ' '.join(parts[:2]) in valid_modifiers:
            access_modifier = ' '.join(parts[:2])
            parts = parts[2:]
        elif parts[0] in valid_modifiers:
            access_modifier = parts.pop(0)
        else:
            access_modifier = ''

        # Extract function type ("Function" or "Sub")
        func_type = parts.pop(0) if len(parts) > 0 else ''
        if func_type not in ('Function', 'Sub'):
            raise ValueError(f'No "Function" or "Sub" in "{sig}".')

        # Extract function name
        func_name = parts.pop(0) if len(parts) > 0 else ''
        if not func_name:
            raise ValueError(f'No Function name in "{sig}".')

        # Add access modifier to signode
        if access_modifier:
            signode += addnodes.desc_annotation(
                access_modifier + ' ', access_modifier + ' ')

        # Add function type to signode
        signode += addnodes.desc_annotation(func_type + ' ', func_type + ' ')

        # Add function name to signode
        signode += addnodes.desc_name(func_name, func_name)

        # Add param list to signode
        paramlist = addnodes.desc_parameterlist()
        for arg in args:
            if ' As ' not in arg:
                raise ValueError(f'No type for arg "{arg}" in "{sig}".')
            name, type_info = arg.split(' As ')
            param = addnodes.desc_parameter('', '')
            param += addnodes.desc_sig_name('', name)
            param += addnodes.desc_sig_punctuation('', ' As ')
            param += addnodes.desc_sig_keyword('', type_info)
            paramlist += param
        signode += paramlist

        # Add return type to signode
        if return_type:
            signode += addnodes.desc_returns(
                ' As ' + return_type, ' As ' + return_type)

        # モジュール名の取得（例：環境変数を利用）
        module_name = self.env.ref_context.get('vb:module')

        # Return Object identifier.
        if module_name:
            return f'{module_name}.{func_name}'
        else:
            return func_name

    def run(self) -> list:
        '''Make a section with function-info nodes from Function directive.
        '''
        sig_result = self.handle_signature(self.arguments[0], self.options)

        # TODO: sig_result は (モジュール名+)関数名 なので、そのように扱う。

        # 関数ノードの作成
        # (太字で強調表示されたアクセス指定子, 関数タイプ, 関数名)
        func_node = nodes.paragraph()
        text = sig_result['func_type'] + ' ' + sig_result['func_name']
        if sig_result['access_modifier']:
            text = sig_result['access_modifier'] + ' ' + text
        func_node += nodes.strong(text=text)

        # 引数ノードの作成 (斜体で強調表示された「引数」)
        args_node = nodes.paragraph()
        args_node += nodes.emphasis(text=f"({sig_result['params']})")

        # 戻り値ノードの作成 (インライン描画される「戻り値の型」)
        return_node = nodes.paragraph()
        return_node += nodes.inline(text=f"As {sig_result['return_type']}")

        # ここまでのノードを含むセクションの作成
        section = nodes.section()
        section += func_node
        section += args_node
        section += return_node

        return [section]

    def add_target_and_index(
            self, name: ObjDescT, sig: str, signode: desc_signature
            ) -> None:
        '''Add cross-reference id and index entry.

        Parameters
        ----------
        name: ObjDescT
            Object name (function name).
        sig: str
            Function declaration from first arg of the directive.
        signode: desc_signature
            Node for signature structure.
        '''
        objects = self.env.domaindata['vb']['objects']
        objects[name] = (self.env.docname, self.objtype, sig)

        super().add_target_and_index(name, sig, signode)


class VBModule(Directive):
    '''For module directive (vb:module).
    '''
    # Class variables are module directive's specs.
    has_content = True  # for module summary or details.
    required_arguments = 1  # 1 arg is enough as whole declaration.
    option_spec = {}

    def run(self):
        pass

    def parse_arguments(self):
        pass

    def parse_options(self):
        pass


class VBDomain(Domain):
    '''Domain for Visual Basic.
    '''
    name = 'vb'
    label = 'Visual Basic'

    directives = {
        'function': VBFunction,
        'module': VBModule,
    }
    roles = {
        'func': VBXRefRole(),
    }

    # autodoc で使われる情報を保持する辞書の、初期値
    initial_data = {
        "functions": {},  # function name -> (docname, synopsis)
        "classes": {},    # class name -> (docname, synopsis)
        "modules": {},    # module name -> (docname, synopsis)
    }

    def get_objects(self) -> None:
        return super().get_objects()

    def resolve_xref(
            self, env: BuildEnvironment, fromdocname: str, builder: Builder,
            typ: str, target: str, node: pending_xref, contnode: Element,
            ) -> Element | None:
        return super().resolve_xref(
            env, fromdocname, builder, typ, target, node, contnode)

    def process_doc(
            self, env: BuildEnvironment, docname: str,
            document: nodes.document) -> None:
        super().process_doc(env, docname, document)
