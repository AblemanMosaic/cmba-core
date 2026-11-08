"""Small deterministic public examples; no signing identity or production authority."""
from .bindings import bind, dimension, profile_reference
from .registry import contract
from .evaluation import context_for


def bundle(profile_id, values):
    c=contract(profile_id)
    dims=[dimension(d['dimension_id'],d['role'],d['schema_id'],values[d['dimension_id']]) for d in c['required_dimensions']]
    binding=bind(profile_reference(c),dims)
    return {'schema':'cmba.workbench-bundle.v0.1-i1','binding':binding,'values':values,
            'context':context_for(binding,epoch=100)}


def chc(*, wrong_output=False):
    return bundle('cmba.chc.transform', {
        'input':{'text':'{ "b": 2, "a": 1 }'},
        'rule':{'operation':'canonical-json','version':1},
        'toolchain':{'engine':'cmba.builtin.cjson','codec':'cmba-cjson-i1'},
        'output':{'text':'{"a":1,"b":99}' if wrong_output else '{"a":1,"b":2}'}})


def session():
    text='Decision: preserve DKN bytes. Reconsider after independent review.\n'
    quote='preserve DKN bytes'
    start=text.encode('utf-8').index(quote.encode('utf-8'))
    return bundle('cmba.gendev.session', {'source':{'text':text},'events':[
        {'event_id':'decision-1','kind':'decision','start_byte':start,'end_byte':start+len(quote.encode()),
         'quote':quote,'attributed_to':'demo.author','interpretation':'Preserve the frozen DKN baseline.',
         'coverage':'ATTRIBUTED_PARTIAL_EXTRACTION'}]})
