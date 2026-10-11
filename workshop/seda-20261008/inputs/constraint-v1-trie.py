"""Isolated, bounded selection of reviewed claims; no completion repair."""
import hashlib,json,sys
from app.answer.grounding import eligible,validate_claims
from app.answer.validation import validate_shape

def canonical(value):return json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':'))
def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
class Trie:
    def __init__(self,texts,tokenizer,eos):
        self.texts=texts;self.paths=[];self.root={};self.edges=0
        for text in texts:
            ids=tokenizer(text,add_special_tokens=False,truncation=False)['input_ids']+[eos]
            if len(ids)>384 or len(text.encode())>16384 or tokenizer.decode(ids,skip_special_tokens=True)!=text:raise ValueError('path_budget_or_roundtrip')
            node=self.root
            for token in ids:
                if token not in node:node[token]={};self.edges+=1
                node=node[token]
            self.paths.append(ids)
        def size(node):return sys.getsizeof(node)+sum(sys.getsizeof(k)+size(v) for k,v in node.items())
        self.storage_bytes=size(self.root)+sys.getsizeof(self.paths)+sum(sys.getsizeof(p)+sum(sys.getsizeof(i) for i in p) for p in self.paths)+sys.getsizeof(texts)+sum(sys.getsizeof(t) for t in texts)
        if self.edges>768 or self.storage_bytes>1048576:raise ValueError('trie_budget')
        self.sha256=digest(self.paths)
        self.branch_observations=[]
    def allowed(self,prefix):
        node=self.root
        for token in prefix:
            if int(token) not in node:raise ValueError('invalid_constraint_prefix')
            node=node[int(token)]
        if not node:raise ValueError('empty_constraint_prefix')
        return sorted(node)
    def callback(self,prompt_length):
        def allow(batch,ids):
            if batch!=0 or len(ids)<prompt_length:raise ValueError('invalid_batch_or_length')
            prefix=ids[prompt_length:].tolist() if hasattr(ids,'tolist') else ids[prompt_length:]
            result=self.allowed(prefix)
            if len(result)>1:self.branch_observations.append({'new_token_position':len(prefix),'allowed_token_ids':result})
            return result
        return allow

def compile_choices(context,binding,tokenizer,eos):
    if digest(context)!=digest(binding['context']):raise ValueError('context_binding_mismatch')
    evidence=context['evidence']
    required=eligible(binding['catalog'],binding['scope'],context['question'],binding['snapshot'],evidence)
    if len(required)!=1 or context['rules']!=[{'claim_id':r['claim_id'],'text':r['text']} for r in required]:raise ValueError('reviewed_rule_binding')
    if len({p['chunk_id'] for p in evidence})!=len(evidence):raise ValueError('duplicate_chunk_ids')
    choices=[]
    for passage in evidence:
        candidate={'status':'answered','claims':[{'claim_id':required[0]['claim_id'],'text':required[0]['text'],'chunk_ids':[passage['chunk_id']]}],'reason':None}
        try:validate_claims(candidate,required,evidence)
        except ValueError:continue
        choices.append(candidate)
    if len(choices)!=1:raise ValueError('ambiguous_or_missing_support')
    choices.append({'status':'insufficient_evidence','claims':[],'reason':'unsupported_question'})
    for choice in choices:validate_shape(choice,'ModelResponse')
    return Trie([canonical(c) for c in choices],tokenizer,eos)
