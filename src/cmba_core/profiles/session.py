"""Recorded-session provenance, never hidden reasoning or automatic truth extraction."""
from ..bindings import exact, identifier
from ..errors import require


def evaluate(values: dict) -> dict:
    exact(values['source'], {'text'})
    require(type(values['source']['text']) is str, 'CMBA_SESSION_TEXT')
    raw=values['source']['text'].encode('utf-8')
    events=values['events']
    require(type(events) is list and 1<=len(events)<=256, 'CMBA_SESSION_EVENT_LIMIT')
    seen=set();matching=True
    for e in events:
        exact(e, {'event_id','kind','start_byte','end_byte','quote','attributed_to','interpretation','coverage'})
        identifier(e['event_id']);identifier(e['kind']);identifier(e['attributed_to'])
        require(e['event_id'] not in seen, 'CMBA_SESSION_EVENT_DUPLICATE');seen.add(e['event_id'])
        require(type(e['start_byte']) is int and type(e['end_byte']) is int and
                0<=e['start_byte']<e['end_byte']<=len(raw), 'CMBA_SESSION_SPAN')
        require(type(e['quote']) is str and type(e['interpretation']) is str, 'CMBA_SESSION_TEXT')
        require(e['coverage']=='ATTRIBUTED_PARTIAL_EXTRACTION', 'CMBA_SESSION_COVERAGE')
        matching=matching and raw[e['start_byte']:e['end_byte']]==e['quote'].encode('utf-8')
    return {'session.source-spans':'MATCH' if matching else 'CONTRADICTED',
            'session.attribution':'MATCH'}
