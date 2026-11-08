"""Headless J1 workbench integration seam. Native UI integration is Batch K.

Opening a document cannot register code or adopt its authority context implicitly.
"""
from cmba_core import inspect, canonical, Refusal
from cmba_core.codec import clone
from cmba_core.bindings import exact
from cmba_core.errors import require
from cmba_core.j1.evaluation import evaluate,replay
from cmba_core.j1.registry import capabilities

class Applications:
    def __init__(self):
        self._bundle=None;self._receipt=None;self._context=None

    def load(self,bundle):
        self._bundle=None;self._receipt=None;self._context=None
        exact(bundle, {'schema','binding','values','context'})
        require(bundle['schema']=='cmba.workbench-bundle.j1','CMBA_J_BUNDLE_SCHEMA')
        result=inspect(bundle['binding'],bundle['values']);self._bundle=clone(bundle);return result

    def evaluate(self, *, reader_context=None, accept_document_context=False):
        self._receipt=None;self._context=None
        require(type(accept_document_context) is bool,'CMBA_ARGUMENT_TYPE')
        require(self._bundle is not None,'CMBA_NO_SELECTION')
        require(reader_context is not None or accept_document_context,'CMBA_READER_CONTEXT_REQUIRED')
        context=clone(reader_context if reader_context is not None else self._bundle['context'])
        receipt=evaluate(self._bundle['binding'],self._bundle['values'],context)
        self._context=context;self._receipt=clone(receipt);return receipt

    def replay(self):
        require(self._bundle is not None and self._receipt is not None,'CMBA_NO_RECEIPT')
        return replay(self._receipt,self._bundle['binding'],self._bundle['values'],self._context)

    def capabilities(self):return capabilities()
