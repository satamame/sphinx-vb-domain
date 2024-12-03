from docutils import nodes
from docutils.nodes import Element
from sphinx.addnodes import pending_xref, desc_signature
from sphinx.builders import Builder
from sphinx.directives import ObjectDescription, ObjDescT
from sphinx.domains import Domain
from sphinx.environment import BuildEnvironment


class VBDomain(Domain):
    '''Domain for Visual Basic
    '''
    name = 'vb'

    class VBFunction(ObjectDescription):
        has_content = True
        required_arguments = 1
        option_spec = {

        }

        def handle_signature(
                self, sig: str, signode: desc_signature) -> ObjDescT:
            super().handle_signature(sig, signode)

        def add_target_and_index(
                self, name: ObjDescT, sig: str, signode: desc_signature
                ) -> None:
            super().add_target_and_index(name, sig, signode)

    directives = {
        'function': VBFunction,
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
