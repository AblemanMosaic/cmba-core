"""One actually recomputed transformation, deliberately not a compiler theorem."""
from ..bindings import exact
from ..codec import decode, canonical
from ..errors import require


def evaluate(values: dict) -> dict:
    for key in ('input','output'):
        exact(values[key], {'text'})
        require(type(values[key]['text']) is str, 'CMBA_CHC_TEXT_TYPE')
    exact(values['rule'], {'operation','version'})
    exact(values['toolchain'], {'engine','codec'})
    supported=(canonical(values['rule'])==canonical({'operation':'canonical-json','version':1}) and
               canonical(values['toolchain'])==canonical({'engine':'cmba.builtin.cjson','codec':'cmba-cjson-i1'}))
    if not supported:
        return {'chc.supported-rule':'UNSUPPORTED','chc.recomputed-output':'NOT_CHECKED'}
    parsed=decode(values['input']['text'].encode('utf-8'), canonical_required=False)
    expected=canonical(parsed).decode('utf-8')
    return {'chc.supported-rule':'MATCH',
            'chc.recomputed-output':'MATCH' if expected==values['output']['text'] else 'CONTRADICTED'}
