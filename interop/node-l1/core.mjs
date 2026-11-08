/* Same-author, separately written SMALL-CORE verification realization.
 * No Python subprocess/import, npm dependency, profiles, signatures, GUI, or effects.
 * Implements the six frozen I1 conformance operations. This is NOT a full CMBA port.
 * BigInt is mandatory: JS Number would lose signed-64-bit JSON integers.
 */
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
const MAX_BYTES=1048576,MAX_STRING=262144,MAX_ITEMS=1024,MAX_NODES=16384,MAX_DEPTH=32;
export class Refusal extends Error { constructor(code){super(code);this.code=code;} }
const req=(v,c)=>{if(!v)throw new Refusal(c);};
const obj=v=>v!==null&&typeof v==='object'&&!Array.isArray(v);
const sorted=arr=>arr.slice().sort((a,b)=>{let aa=Array.from(a,c=>c.codePointAt(0)),bb=Array.from(b,c=>c.codePointAt(0));for(let i=0;i<Math.min(aa.length,bb.length);i++){if(aa[i]!==bb[i])return aa[i]-bb[i];}return aa.length-bb.length;});
const same=(a,b)=>canonical(a).equals(canonical(b));
export function canonical(value){
 let nodes=0,bytes=0;
 function visit(v,d){
  req(d<=MAX_DEPTH,'CMBA_DEPTH_LIMIT');req(++nodes<=MAX_NODES,'CMBA_NODE_LIMIT');
  if(v===null)return 'null';
  if(typeof v==='boolean')return v?'true':'false';
  if(typeof v==='bigint'){req(v>=-(1n<<63n)&&v<(1n<<63n),'CMBA_INTEGER_RANGE');return v.toString();}
  if(typeof v==='number'){req(Number.isSafeInteger(v),'CMBA_VALUE_TYPE');return visitInteger(v);}
  if(typeof v==='string'){
   req(Array.from(v).length<=MAX_STRING,'CMBA_STRING_LIMIT');
   for(const c of v){let n=c.codePointAt(0);req(n<0xd800||n>0xdfff,'CMBA_STRING_INVALID');}
   let size=Buffer.byteLength(v,'utf8');req(size<=MAX_STRING,'CMBA_STRING_LIMIT');bytes+=size;req(bytes<=MAX_BYTES,'CMBA_BYTE_LIMIT');
   return JSON.stringify(v);
  }
  if(Array.isArray(v)){req(v.length<=MAX_ITEMS,'CMBA_COLLECTION_LIMIT');return '['+v.map(x=>visit(x,d+1)).join(',')+']';}
  req(obj(v),'CMBA_VALUE_TYPE');let keys=Object.keys(v);req(keys.length<=MAX_ITEMS,'CMBA_COLLECTION_LIMIT');
  // Validate/count all keys at the same depth as Python; order cannot alter valid bytes.
  return '{'+sorted(keys).map(k=>visit(k,d+1)+':'+visit(v[k],d+1)).join(',')+'}';
 }
 function visitInteger(v){return String(v);}
 const raw=Buffer.from(visit(value,0),'utf8');req(raw.length<=MAX_BYTES,'CMBA_BYTE_LIMIT');return raw;
}
export function decode(raw,{canonicalRequired=true}={}){
 req(Buffer.isBuffer(raw),'CMBA_BYTES_REQUIRED');req(raw.length<=MAX_BYTES,'CMBA_BYTE_LIMIT');
 let quoted=false,escaped=false,depth=0;
 for(const b of raw){if(quoted){if(escaped)escaped=false;else if(b===92)escaped=true;else if(b===34)quoted=false;}else if(b===34)quoted=true;else if(b===91||b===123){req(++depth<=MAX_DEPTH+1,'CMBA_DEPTH_LIMIT');}else if(b===93||b===125){req(--depth>=0,'CMBA_JSON_INVALID');}}
 let text;try{text=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(raw);}catch{throw new Refusal('CMBA_JSON_INVALID');}
 let p=0;
 const ws=()=>{while(p<text.length&&/[ \t\r\n]/.test(text[p]))p++;};
 const bad=()=>{throw new Refusal('CMBA_JSON_INVALID');};
 function string(){let start=p++;let escaped=false;while(p<text.length){let c=text[p++];if(escaped){escaped=false;continue;}if(c==='\\'){escaped=true;continue;}if(c==='"'){try{return JSON.parse(text.slice(start,p));}catch{bad();}}}bad();}
 function val(){ws();if(p>=text.length)bad();let ch=text[p];
  if(ch==='"')return string();
  if(ch==='['){p++;let a=[];ws();if(text[p]===']'){p++;return a;}while(true){a.push(val());ws();if(text[p]===']'){p++;return a;}if(text[p++]!==',')bad();}}
  if(ch==='{'){p++;let o=Object.create(null);ws();if(text[p]==='}'){p++;return o;}while(true){ws();if(text[p]!=='"')bad();let k=string();ws();if(text[p++]!==':')bad();let v=val();req(!Object.hasOwn(o,k),'CMBA_DUPLICATE_KEY');o[k]=v;ws();if(text[p]==='}'){p++;return o;}if(text[p++]!==',')bad();}}
  for(const [word,v] of [['true',true],['false',false],['null',null]])if(text.startsWith(word,p)){p+=word.length;return v;}
  for(const word of ['NaN','Infinity','-Infinity'])if(text.startsWith(word,p))throw new Refusal('CMBA_NUMBER_INVALID');
  let m=/^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/.exec(text.slice(p));
  if(!m)bad();p+=m[0].length;req(!/[.eE]/.test(m[0]),'CMBA_NUMBER_INVALID');return BigInt(m[0]);
 }
 let result=val();ws();req(p===text.length,'CMBA_JSON_INVALID');let encoded=canonical(result);
 if(canonicalRequired)req(encoded.equals(raw),'CMBA_NOT_CANONICAL');return result;
}
const exact=(v,keys)=>req(obj(v)&&Object.keys(v).length===keys.length&&keys.every(k=>Object.hasOwn(v,k)),'CMBA_FIELDS_INVALID');
const ident=v=>{req(typeof v==='string'&&/^[a-z][a-z0-9._:/-]{0,191}$/.test(v),'CMBA_IDENTIFIER_INVALID');return v;};
const hex=v=>{req(typeof v==='string'&&/^[0-9a-f]{64}$/.test(v),'CMBA_DIGEST_INVALID');return v;};
export const digest=(domain,v)=>createHash('sha256').update(Buffer.from('CMBA:I1:'+domain+'\0','ascii')).update(canonical(v)).digest('hex');
const clone=v=>decode(canonical(v));
const pr=v=>{exact(v,['profile_id','profile_version','contract_hash']);ident(v.profile_id);ident(v.profile_version);hex(v.contract_hash);};
const ref=v=>{exact(v,['scheme','algorithm','digest_hex']);ident(v.scheme);hex(v.digest_hex);req(['SHA-256','BLAKE3-256'].includes(v.algorithm),'CMBA_REFERENCE_ALGORITHM');};
function dim(v){exact(v,['dimension_id','role','schema_id','codec','algorithm','critical','value_hash']);for(const k of ['dimension_id','role','schema_id'])ident(v[k]);req(v.codec==='cmba-cjson-i1'&&v.algorithm==='SHA-256','CMBA_ENCODING_UNSUPPORTED');req(typeof v.critical==='boolean','CMBA_CRITICAL_TYPE');hex(v.value_hash);}
function valueBody(v,value){return {dimension_id:v.dimension_id,role:v.role,schema_id:v.schema_id,codec:v.codec,algorithm:v.algorithm,critical:v.critical,value};}
export function dimension(a){for(const k of ['dimension_id','role','schema_id'])ident(a[k]);req(typeof a.critical==='boolean','CMBA_CRITICAL_TYPE');let v={dimension_id:a.dimension_id,role:a.role,schema_id:a.schema_id,codec:'cmba-cjson-i1',algorithm:'SHA-256',critical:a.critical};return {...v,value_hash:digest('dimension-value',valueBody(v,a.value))};}
function rel(r){exact(r,['relation_id','predicate','target']);ident(r.relation_id);ident(r.predicate);ref(r.target);}
function body(b){exact(b,['schema','profile','dimensions','relations']);req(b.schema==='cmba.binding-body.v0.1-i1','CMBA_SCHEMA_UNSUPPORTED');pr(b.profile);
 req(Array.isArray(b.dimensions)&&b.dimensions.length>=1&&b.dimensions.length<=64,'CMBA_DIMENSION_LIMIT');req(Array.isArray(b.relations)&&b.relations.length<=256,'CMBA_RELATION_LIMIT');b.dimensions.forEach(dim);
 let n=b.dimensions.map(d=>d.dimension_id);req(new Set(n).size===n.length,'CMBA_DIMENSION_DUPLICATE');req(same(n,sorted(n)),'CMBA_DIMENSION_ORDER');
 b.relations.forEach(rel);n=b.relations.map(r=>r.relation_id);req(new Set(n).size===n.length,'CMBA_RELATION_DUPLICATE');req(same(n,sorted(n)),'CMBA_RELATION_ORDER');
}
export function bind(a){pr(a.profile);req(Array.isArray(a.dimensions)&&a.dimensions.length>=1&&a.dimensions.length<=64,'CMBA_DIMENSION_LIMIT');req(a.relations===null||(Array.isArray(a.relations)&&a.relations.length<=256),'CMBA_RELATION_LIMIT');a.dimensions.forEach(dim);let rs=a.relations===null?[]:clone(a.relations);rs.forEach(rel);
 let b={schema:'cmba.binding-body.v0.1-i1',profile:clone(a.profile),dimensions:clone(a.dimensions),relations:rs.sort((a,b)=>a.relation_id<b.relation_id?-1:a.relation_id>b.relation_id?1:0)};
 // Identifiers use ASCII and must follow codepoint order, not locale collation.
 b.dimensions.sort((a,b)=>a.dimension_id<b.dimension_id?-1:a.dimension_id>b.dimension_id?1:0);
 body(b);return {schema:'cmba.binding.v0.1-i1',body:b,binding_root:digest('binding-root',b)};
}
export function validateBinding(b){canonical(b);exact(b,['schema','body','binding_root']);req(b.schema==='cmba.binding.v0.1-i1','CMBA_SCHEMA_UNSUPPORTED');body(b.body);hex(b.binding_root);req(digest('binding-root',b.body)===b.binding_root,'CMBA_BINDING_MISMATCH');}
export function inspect(a){let b=a.binding;validateBinding(b);if(a.expected_root!==null){hex(a.expected_root);req(b.binding_root===a.expected_root,'CMBA_EXPECTED_ROOT_MISMATCH');}
 let values=a.values===null?Object.create(null):a.values;req(obj(values),'CMBA_VALUES_TYPE');canonical(values);let ds=b.body.dimensions;req(Object.keys(values).every(k=>ds.some(d=>d.dimension_id===k)),'CMBA_UNBOUND_VALUE');let rows=[];
 for(const d of ds){let supplied=Object.hasOwn(values,d.dimension_id);if(supplied)req(digest('dimension-value',valueBody(d,values[d.dimension_id]))===d.value_hash,'CMBA_DIMENSION_MISMATCH');rows.push({dimension_id:d.dimension_id,role:d.role,schema_id:d.schema_id,critical:d.critical,commitment:supplied?'MATCH':'NOT_SUPPLIED',semantics:'NOT_EVALUATED'});}
 return {schema:'cmba.inspection.v0.1-i1',status:'BINDING_STRUCTURE_VALID',binding_root:b.binding_root,profile:clone(b.body.profile),external_anchor:a.expected_root===null?'NOT_PROVIDED':'MATCHED_CALLER_EXPECTATION',dimensions:rows,relations:clone(b.body.relations),relation_targets:'NOT_RESOLVED',signature:'NOT_CHECKED',authority_effect:'NONE',semantic_truth:'NOT_ESTABLISHED'};
}
export function compare(a){let l=a.left,r=a.right;validateBinding(l);validateBinding(r);
 function diffs(field,key){let aa=new Map(l.body[field].map(v=>[v[key],v])),bb=new Map(r.body[field].map(v=>[v[key],v]));return sorted([...new Set([...aa.keys(),...bb.keys()])]).filter(k=>!aa.has(k)||!bb.has(k)||!same(aa.get(k),bb.get(k))).map(k=>({id:k,change:!aa.has(k)?'ADDED':!bb.has(k)?'REMOVED':'CHANGED'}));}
 return {schema:'cmba.comparison.v0.1-i1',left_root:l.binding_root,right_root:r.binding_root,same_binding:l.binding_root===r.binding_root,same_profile:same(l.body.profile,r.body.profile),dimension_changes:diffs('dimensions','dimension_id'),relation_changes:diffs('relations','relation_id'),semantic_equivalence:'NOT_ESTABLISHED',authority_effect:'NONE'};
}
export function dispatch(r){try{
 exact(r,['operation','arguments']);let a=r.arguments;req(obj(a),'CMBA_ARGUMENT_TYPE');let value;
 if(r.operation==='canonical'){exact(a,['value']);value={hex:canonical(a.value).toString('hex')};}
 else if(r.operation==='decode'){exact(a,['hex']);req(typeof a.hex==='string','CMBA_BYTES_REQUIRED');req(/^(?:[ \t\r\n\v\f]*[0-9a-fA-F]{2})*[ \t\r\n\v\f]*$/.test(a.hex),'CMBA_BYTES_REQUIRED');let h=a.hex.replace(/[ \t\r\n\v\f]/g,'');value=decode(Buffer.from(h,'hex'));}
 else if(r.operation==='dimension'){exact(a,['dimension_id','role','schema_id','value','critical']);value=dimension(a);}
 else if(r.operation==='bind'){exact(a,['profile','dimensions','relations']);value=bind(a);}
 else if(r.operation==='inspect'){exact(a,['binding','values','expected_root']);value=inspect(a);}
 else if(r.operation==='compare'){exact(a,['left','right']);value=compare(a);}
 else throw new Refusal('CMBA_OPERATION_UNSUPPORTED');
 return {status:'RESULT',value};
 }catch(e){if(e instanceof Refusal)return {status:'REFUSED',code:e.code};throw e;}}
export function main(raw){const r=decode(raw);exact(r,['schema','requests']);req(r.schema==='cmba.conformance-requests.i1','CMBA_REQUEST_SCHEMA');req(Array.isArray(r.requests)&&r.requests.length<=256,'CMBA_COLLECTION_LIMIT');return canonical({schema:'cmba.conformance-results.i1',results:r.requests.map(dispatch)});}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){try{let raw=readFileSync(0);req(raw.length<=MAX_BYTES,'CMBA_BYTE_LIMIT');process.stdout.write(Buffer.concat([main(raw),Buffer.from('\n')]));}catch(e){if(!(e instanceof Refusal))throw e;process.stdout.write(canonical({status:'REFUSED',code:e.code}));process.exitCode=2;}}
