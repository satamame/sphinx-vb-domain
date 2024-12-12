import re

from docutils import nodes
from docutils.nodes import Element
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.addnodes import pending_xref, desc_signature
from sphinx.builders import Builder
from sphinx.directives import ObjectDescription, ObjDescT
from sphinx.domains import Domain
from sphinx.environment import BuildEnvironment


class VBDomain(Domain):
    '''Domain for Visual Basic
    '''
    name = 'vb'
    label = 'Visual Basic'

    class VBFunction(ObjectDescription):
        '''For function directive (vb:function)
        '''
        # Class variables are function directive's specs.
        has_content = True  # for function summary or details.
        required_arguments = 1  # 1 arg is enough as whole declaration.
        option_spec = {
            'param': directives.unchanged,
            'type': directives.unchanged,
            'returns': directives.unchanged,
        }

        def handle_signature(self, sig, signode):
            '''Parse the function signature and add nodes to the signode.
            '''
            # Split signature into 3 parts
            match = re.match(r'^(.*?)\s*(\(.*?\))?\s*(As\s+.+)?$', sig)
            if not match:
                raise ValueError(f"Invalid signature: {sig}")

            # Part 1: access modifier and function name
            access_and_name = match.group(1).strip()
            # Part 2: parameters (without ())
            params = match.group(2).strip("()") if match.group(2) else ""
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

            func_type = parts.pop(0)  # "Function" or "Sub"
            func_name = parts.pop(0)  # e.g., "MyFunction"

            # Add function name to the signode for rendering
            signode += addnodes.desc_name(func_name, func_name)

            # Return the parsed information as a tuple or dictionary
            return {
                'access_modifier': access_modifier,
                'func_type': func_type,
                'func_name': func_name,
                'params': params,
                'return_type': return_type,
            }

        def add_target_and_index(
                self, name: ObjDescT, sig: str, signode: desc_signature
                ) -> None:
            super().add_target_and_index(name, sig, signode)

    directives = {'function': VBFunction}

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
