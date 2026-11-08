import pytest
from cmba_core import canonical, decode, Refusal
from cmba_core.codec import MAX_BYTES, MAX_ITEMS

@pytest.mark.parametrize('value,expected',[
 (None,b'null'),(False,b'false'),(True,b'true'),(0,b'0'),(-1,b'-1'),
 (2**63-1,b'9223372036854775807'),(-2**63,b'-9223372036854775808'),
 ('é','"é"'.encode()),('\n',b'"\\n"'),('a"b',b'"a\\"b"'),
 ([],b'[]'),({},b'{}'),({'z':1,'a':False},b'{"a":false,"z":1}'),
 ({'\U00010000':1,'\ue000':2},'{"\ue000":2,"\U00010000":1}'.encode()),
 ([None,False,0],b'[null,false,0]'),('e\u0301','"e\u0301"'.encode())])
def test_canonical_known(value,expected):
    assert canonical(value)==expected
    assert canonical(decode(expected))==expected

@pytest.mark.parametrize('value,code',[
 (1.0,'CMBA_VALUE_TYPE'),(float('nan'),'CMBA_VALUE_TYPE'),(2**63,'CMBA_INTEGER_RANGE'),
 (-2**63-1,'CMBA_INTEGER_RANGE'),(b'a','CMBA_VALUE_TYPE'),((1,),'CMBA_VALUE_TYPE'),
 ({1:'a'},'CMBA_OBJECT_KEY'),('\ud800','CMBA_STRING_INVALID'),
 ([0]*(MAX_ITEMS+1),'CMBA_COLLECTION_LIMIT'),('x'*(256*1024+1),'CMBA_STRING_LIMIT')],
 ids=['float','nan','integer-high','integer-low','bytes','tuple','non-string-key','surrogate',
      'collection-limit','string-limit'])
def test_invalid_value(value,code):
    with pytest.raises(Refusal,match=code):canonical(value)

@pytest.mark.parametrize('raw,code',[
 (b'{"a":1,"a":2}','CMBA_DUPLICATE_KEY'),(b'1.0','CMBA_NUMBER_INVALID'),
 (b'NaN','CMBA_NUMBER_INVALID'),(b'Infinity','CMBA_NUMBER_INVALID'),
 (b'9223372036854775808','CMBA_INTEGER_RANGE'),(b'{','CMBA_JSON_INVALID'),
 (b'\xff','CMBA_JSON_INVALID'),(b'\xef\xbb\xbf{}','CMBA_JSON_INVALID'),
 (b' null','CMBA_NOT_CANONICAL'),(b'null\n','CMBA_NOT_CANONICAL'),
 (b'-0','CMBA_NOT_CANONICAL'),(b'"\\u0061"','CMBA_NOT_CANONICAL'),
 (b'{"z":1,"a":2}','CMBA_NOT_CANONICAL'),(b'"\\ud800"','CMBA_STRING_INVALID'),
 (b'['*40+b'0'+b']'*40,'CMBA_DEPTH_LIMIT'),(b' '* (MAX_BYTES+1),'CMBA_BYTE_LIMIT')],
 ids=['duplicate-key','float','nan','infinity','integer-range','truncated','invalid-utf8','bom',
      'leading-space','trailing-newline','negative-zero','escaped-ascii','key-order','surrogate',
      'depth-limit','byte-limit'])
def test_rejected_encoding(raw,code):
    with pytest.raises(Refusal,match=code):decode(raw)

def test_explicit_authoring_mode_not_implicit_fallback():
    assert decode(b' {"z": 1, "a":2} ',canonical_required=False)=={'a':2,'z':1}
    with pytest.raises(Refusal):decode(b'{"a":1,"a":2}',canonical_required=False)

def test_unicode_not_normalized():
    assert canonical('é')!=canonical('e\u0301')

def test_json_subclass_refused():
    class SneakyInt(int):pass
    with pytest.raises(Refusal):canonical(SneakyInt(1))

def test_cycle_is_bounded():
    value=[];value.append(value)
    with pytest.raises(Refusal,match='CMBA_DEPTH_LIMIT'):canonical(value)

def test_node_budget():
    with pytest.raises(Refusal,match='CMBA_NODE_LIMIT'):canonical([[0]*1024]*17)

def test_total_bytes():
    with pytest.raises(Refusal,match='CMBA_BYTE_LIMIT'):canonical(['a'*(256*1024)]*5)
