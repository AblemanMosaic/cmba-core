"""Headless, testable view model. Imported data cannot add capabilities."""
from cmba_core.bindings import exact, inspect
from cmba_core.codec import clone
from cmba_core.evaluation import evaluate, replay
from cmba_core.registry import catalogue, capability_descriptors
from cmba_core.errors import require


class Workbench:
    def __init__(self):
        self._bundle=None
        self._receipt=None

    def load(self, bundle: dict) -> dict:
        self._bundle=None; self._receipt=None
        exact(bundle, {'schema','binding','values','context'})
        require(bundle['schema']=='cmba.workbench-bundle.v0.1-i1','CMBA_BUNDLE_SCHEMA')
        # External reader policy is not silently replaced. This context is displayed
        # as document-supplied; evaluation uses it only after an explicit call.
        result=inspect(bundle['binding'],bundle['values'])
        self._bundle=clone(bundle);self._receipt=None
        return result

    def inspect(self):
        require(self._bundle is not None,'CMBA_NO_SELECTION')
        return inspect(self._bundle['binding'],self._bundle['values'])

    def evaluate(self, *, accept_document_context: bool = False, reader_context: dict | None = None):
        self._receipt=None
        require(self._bundle is not None,'CMBA_NO_SELECTION')
        require(type(accept_document_context) is bool,'CMBA_ARGUMENT_TYPE')
        require(reader_context is not None or accept_document_context,'CMBA_READER_CONTEXT_REQUIRED')
        context=clone(reader_context if reader_context is not None else self._bundle['context'])
        receipt=evaluate(self._bundle['binding'],self._bundle['values'],context)
        self._receipt=clone(receipt)
        self._last_context=context
        return receipt

    def replay(self):
        require(self._bundle is not None and self._receipt is not None,'CMBA_NO_RECEIPT')
        return replay(self._receipt,self._bundle['binding'],self._bundle['values'],self._last_context)

    def selected(self):
        require(self._bundle is not None,'CMBA_NO_SELECTION')
        return clone(self._bundle)

    def applications(self):
        return catalogue()

    def capabilities(self):
        return capability_descriptors()
