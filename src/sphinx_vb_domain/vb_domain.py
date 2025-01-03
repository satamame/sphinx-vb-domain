import re

from docutils import nodes
from docutils.nodes import Element
from docutils.parsers.rst import directives, Directive
from sphinx import addnodes
from sphinx.addnodes import pending_xref, desc_signature
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.directives import ObjectDescription, ObjDescT
from sphinx.domains import Domain
from sphinx.environment import BuildEnvironment
from sphinx.roles import XRefRole
from sphinx.util.docfields import Field, TypedField, DocFieldTransformer
from sphinx.util.nodes import make_id

__version__ = '0.1.0'


class VBXRefRole(XRefRole):
    '''For VBDomain's cross-reference e.g. func role (vb:func).
    '''
    # Visual Basic 固有のリンク処理が必要な場合は process_link() を
    # オーバーライドする。
    # TODO: 不要ならこのクラスを削除する。
    pass


class VBFunction(ObjectDescription):
    '''For function directive (vb:function).
    '''
    # Class variables are function directive's specs.
    has_content = True  # for function summary or details.
    required_arguments = 1  # 1 arg is enough as whole declaration.
    option_spec = {
        'param': directives.unchanged,
        'type': directives.unchanged,
        'returns': directives.unchanged,
        'rtype': directives.unchanged,
    }

    doc_field_types = [
        TypedField(
            'parameter', label='パラメータ',
            names=('param', 'parameter', 'arg', 'argument'),
            typerolename='vbtype', typenames=('type',)),
        Field('returnvalue', label='戻り値', has_arg=False,
              names=('returns', 'return')),
        Field('returntype', label='戻り値の型', has_arg=False,
              names=('rtype',)),
    ]

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
        # Split signature into 3 parts.
        match = re.match(r'^(.*?)\s*(\(.*?\))?\s*(As\s+.+)?$', sig)
        if not match:
            raise ValueError(f"Invalid signature: {sig}")

        # Part 1: access modifier and function name.
        access_and_name = match.group(1).strip()
        # Part 2: parameters (without ()).
        parameters = match.group(2).strip("()") if match.group(2) else ""
        args = [arg.strip() for arg in parameters.split(',')]
        # Part 3: return type.
        return_type = match.group(3).removeprefix("As").strip() \
            if match.group(3) else ""

        # Extract access modifier.
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

        # Extract function type ("Function" or "Sub").
        func_type = parts.pop(0) if len(parts) > 0 else ''
        if func_type not in ('Function', 'Sub'):
            raise ValueError(f'No "Function" or "Sub" in "{sig}".')

        # Extract function name.
        func_name = parts.pop(0) if len(parts) > 0 else ''
        if not func_name:
            raise ValueError(f'No Function name in "{sig}".')

        # Add access modifier to signode (e.g. 'Public ').
        if access_modifier:
            signode += addnodes.desc_annotation(
                access_modifier + ' ', access_modifier + ' ')

        # Add function type to signode (e.g. 'Function ').
        signode += addnodes.desc_annotation(func_type + ' ', func_type + ' ')

        # Add function name to signode (e.g. 'MuFunc').
        signode += addnodes.desc_name(func_name, func_name)

        # Add param list to signode.
        paramlist = addnodes.desc_parameterlist()
        for arg in args:
            if ' As ' not in arg:
                raise ValueError(f'No type for arg "{arg}" in "{sig}".')
            # Add param (e.g. 'ByVal arg1 As Integer').
            param = addnodes.desc_parameter('', arg)
            paramlist += param
        signode += paramlist

        # Add return type to signode (e.g. ' As String').
        if return_type:
            signode += nodes.emphasis(
                ' As ' + return_type, ' As ' + return_type)

        # モジュール名の取得 (例：環境変数を利用).
        module_name = self.env.ref_context.get('vb:module')

        # Return Object identifier.
        if module_name:
            return f'{module_name}.{func_name}'
        else:
            return func_name

    def add_target_and_index(
            self, name: ObjDescT, sig: str, signode: desc_signature
            ) -> None:
        '''Add cross-reference id to signode, and index to index entries.

        Parameters
        ----------
        name: ObjDescT
            Object identifier (module_name.function_name).
        sig: str
            Function declaration from first arg of the directive.
        signode: desc_signature
            Node for signature structure.
        '''
        objects = self.env.domaindata['vb']['objects']
        # Add tuple (document_name, object_type (Function), and signature).
        objects[name] = (self.env.docname, self.objtype, sig)

        # クロスリファレンス用のターゲットを追加.
        node_id = make_id(self.env, self.state.document, self.objtype, name)
        signode['ids'].append(node_id)
        self.state.document.note_explicit_target(signode)

        # インデックスエントリーを追加.
        indextext = f'{name} (VB function)'
        self.indexnode['entries'].append(
            ('single', indextext, node_id, '', None)
        )

    def transform_content(self, contentnode):
        super().transform_content(contentnode)

        transformer = DocFieldTransformer(self)
        transformer.transform_all(contentnode)


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
        'vbtype': XRefRole(innernodeclass=nodes.emphasis),
        'func': VBXRefRole(),
    }

    # autodoc で使われる情報を保持する辞書の、初期値
    initial_data = {
        "functions": {},  # function name -> (docname, synopsis)
        "classes": {},    # class name -> (docname, synopsis)
        "modules": {},    # module name -> (docname, synopsis)
        "objects": {},    # object name -> (docname, objtype, signature)
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


def setup(app: Sphinx):
    '''Set up extension
    '''
    app.add_domain(VBDomain)
