"""Explicit data authoring with installed profiles. No source code from a document."""
from cmba_core import bind,dimension,profile_reference,canonical
from cmba_core.codec import clone
from cmba_core.registry import contract
from cmba_core.evaluation import context_for as i_context
from cmba_core.j1.evaluation import bind_application,context_for as j_context
from cmba_core.j1.registry import contracts
from cmba_core.errors import require
from .session import BUNDLE_I,BUNDLE_J,admit_bundle
from .common import integer


def author(profile_id,record, *, now=0,parameters=None,relations=None):
    integer(now);require(type(record) is dict,'CMBA_K_AUTHOR_RECORD')
    if profile_id=='cmba.generic':
        require(parameters in (None,{}),'CMBA_K_AUTHOR_PARAMETERS')
        b=bind(profile_reference(contract(profile_id)),
               [dimension('description','metadata','cmba.author-description.k1',record,critical=False)],relations=relations)
        out={'schema':BUNDLE_I,'binding':b,'values':{'description':clone(record)},'context':i_context(b,epoch=now)}
    else:
        require(profile_id in {c['profile_id'] for c in contracts()},'CMBA_K_AUTHOR_PROFILE')
        v=bind_application(profile_id,record)
        if relations is not None:
            v['binding']=bind(v['binding']['body']['profile'],v['binding']['body']['dimensions'],relations=relations)
        out={'schema':BUNDLE_J,**v,'context':j_context(v['binding'],now=now,parameters=parameters)}
    admit_bundle(out);return out


def example(profile_id):
    """Explicit user-selected PUBLIC fixtures; never production signing or key custody."""
    from cmba_core.j1 import demo
    functions={
      'cmba.chc.graph':demo.graph,'cmba.gendev.rich-session':demo.session,'cmba.kasd':demo.kasd,
      'cmba.consent':demo.consent,'cmba.disclosure':demo.disclosure,'cmba.observation':demo.observation,
      'cmba.coordination':demo.coordination,'cmba.reconciliation':demo.reconciliation,
      'cmba.execution-record':demo.execution,'cmba.claim-trace':demo.trace,'cmba.endorsements':demo.endorsement,
      'cmba.admissibility':demo.admissibility,'cmba.native-dkn':demo.native}
    if profile_id=='cmba.generic':return author('cmba.generic',{'description':'Edit this declaration; meaning is not proved by its hash.'})
    require(profile_id in functions,'CMBA_K_AUTHOR_PROFILE')
    try:value=functions[profile_id]()
    except ImportError:
        from cmba_core import Refusal
        raise Refusal('CMBA_K_OPTIONAL_DEPENDENCY_UNAVAILABLE')
    out={'schema':BUNDLE_J,**value};admit_bundle(out);return out
