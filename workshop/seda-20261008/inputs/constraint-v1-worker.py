import json,os,socket,sys,time,hashlib,runpy
from pathlib import Path
sys.path.insert(0,'/app')
import app.answer.generation as g
proposal=json.loads(Path('/input/generation-prompt-v3-candidate.json').read_text())
assert hashlib.sha256(proposal['system_prompt'].encode()).hexdigest()==proposal['system_prompt_sha256']
report={'stdout_bytes':0,'stderr_bytes':0,'proposal_file_sha256':hashlib.sha256(Path('/input/generation-prompt-v3-candidate.json').read_bytes()).hexdigest(),'system_prompt_sha256':proposal['system_prompt_sha256']}
class Counter:
    def __init__(self,key):self.key=key
    def write(self,text):report[self.key]+=len(text.encode());return len(text)
    def flush(self):pass
    def isatty(self):return False
sys.stdout=Counter('stdout_bytes');sys.stderr=Counter('stderr_bytes')
trie_module=runpy.run_path('/input/constraint-v1-trie.py')
binding=json.loads(Path('/tmp/constraint-v1-binding.json').read_text())
report.update(nonce=binding['nonce'],worker_pid=os.getpid(),helper_sha256={name:hashlib.sha256(Path('/input',name).read_bytes()).hexdigest() for name in ('constraint-v1-worker.py','constraint-v1-trie.py')})
original=g._load_components
class Tokenizer:
    def __init__(self,inner):self.inner=inner
    def __getattr__(self,name):return getattr(self.inner,name)
    def apply_chat_template(self,*a,**kw):
        messages=a[0];report['user_context']=json.loads(messages[1]['content']);assert len(messages)==2 and messages[0]['role']=='system' and messages[1]['role']=='user'
        report['original_system_prompt_sha256']=hashlib.sha256(messages[0]['content'].encode()).hexdigest()
        report['context_sha256']=hashlib.sha256(messages[1]['content'].encode()).hexdigest()
        changed=[{**messages[0],'content':proposal['system_prompt']},messages[1]]
        text=self.inner.apply_chat_template(changed,*a[1:],**kw);report['prompt_bytes']=len(text.encode());report['rendered_input']=text;report['rendered_input_sha256']=hashlib.sha256(text.encode()).hexdigest();report['chat_template_sha256']=hashlib.sha256(self.inner.chat_template.encode()).hexdigest();return text
    def __call__(self,*a,**kw):
        value=self.inner(*a,**kw);report['prompt_tokens']=value['input_ids'].shape[-1];report['input_token_ids']=value['input_ids'][0].tolist();report['input_token_ids_sha256']=trie_module['digest'](report['input_token_ids']);return value
    def decode(self,tokens,**kw):
        text=self.inner.decode(tokens,**kw);report['decoded_tokens']=len(tokens);report['decoded_bytes']=len(text.encode());return text
class Model:
    def __init__(self,inner,tok):self.inner,self.tok=inner,tok
    def generate(self,**kw):
        report['settings']={k:kw[k] for k in ('max_new_tokens','do_sample','num_beams','eos_token_id','pad_token_id')}
        compile_start=time.monotonic()
        catalog=json.loads(Path('/fixtures/grounding-catalog.json').read_text())
        assert binding['catalog']==catalog
        trie=trie_module['compile_choices'](report['user_context'],binding,self.tok,kw['eos_token_id'][0])
        report['compilation_ms']=(time.monotonic()-compile_start)*1000
        report['constraint_sha256']=trie.sha256
        report['constraint_paths']=[{'text':text,'token_ids':ids,'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'new_tokens_including_eos':len(ids)} for text,ids in zip(trie.texts,trie.paths)]
        report['trie_edges']=trie.edges;report['trie_storage_bytes']=trie.storage_bytes
        deadline=float(sys.argv[2]);callback=trie.callback(kw['input_ids'].shape[-1])
        def constrained(batch,ids):
            if time.monotonic()>=deadline:raise g.AnswerError('deadline_exceeded')
            return callback(batch,ids)
        kw['prefix_allowed_tokens_fn']=constrained
        Path('/tmp/constraint-v1-pre-generation.json').write_text(json.dumps(report))
        start=time.monotonic();out=self.inner.generate(**kw);report['generate_ms']=(time.monotonic()-start)*1000
        report['model_generate_calls']=1;report['branch_observations']=trie.branch_observations
        n=kw['input_ids'].shape[-1];tokens=out[0][n:].tolist();report['new_tokens']=len(tokens);report['output_tokens']=out.shape[-1];report['last_token_id']=tokens[-1] if tokens else None
        report['eos_positions']=[i for i,t in enumerate(tokens) if t in kw['eos_token_id']]
        report['tokenizer_eos_positions']=[i for i,t in enumerate(tokens) if t==self.tok.eos_token_id]
        completion=self.tok.decode(tokens,skip_special_tokens=True)
        report['generated_text_bytes']=len(completion.encode())
        report['schema_valid']=False
        if len(completion.encode())<=16384:
            report['raw_output']=completion
            try:
                parsed=g.strict_json(completion);report['strict_json_valid']=True
            except ValueError as error:
                report['strict_json_valid']=False
                causes=[]
                while error is not None and len(causes)<4:
                    causes.append({'type':type(error).__name__,'message':str(error)[:1024]})
                    error=error.__cause__
                report['exact_parser_errors']=causes
            if report.get('strict_json_valid'):
                try:g.validate_shape(parsed,'ModelResponse');report['schema_valid']=True
                except ValueError as error:report['exact_shape_error']={'type':type(error).__name__,'message':str(error)}

        report['stopping_reason']='configured_eos' if tokens and tokens[-1] in kw['eos_token_id'] else 'max_new_tokens' if len(tokens)==kw['max_new_tokens'] else 'other'
        return out
def load(*a,**kw):
    start=time.monotonic();tok,model,torch,effective=original(*a,**kw);report['load_ms']=(time.monotonic()-start)*1000;report['tokenizer_eos_id']=tok.eos_token_id;report['effective_eos_ids']=effective['eos_ids'];report['model_generation_eos']=model.generation_config.eos_token_id if model else None
    return Tokenizer(tok),Model(model,tok) if model else None,torch,effective
g._load_components=load
send=g.send_message
def measured_send(channel,value,deadline):
    if value.get('kind') in ('error','result'):report['worker_response_bytes']=len(json.dumps(value,ensure_ascii=False,allow_nan=False).encode());report['worker_response_kind']=value['kind'];report['worker_error']=value.get('code')
    if value.get('kind') in ('error','result'):Path('/tmp/constraint-v1-diagnostic.json').write_text(json.dumps(report))
    return send(channel,value,deadline)
g.send_message=measured_send
try:
    with socket.socket(fileno=int(sys.argv[1])) as channel:g._module_worker(channel,float(sys.argv[2]))
finally:Path('/tmp/constraint-v1-diagnostic.json').write_text(json.dumps(report))
