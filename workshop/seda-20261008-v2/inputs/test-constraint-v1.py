import copy,json,runpy,unittest
from pathlib import Path
from app.answer.grounding import validate_claims
FIXTURES=Path('/fixtures') if Path('/fixtures/grounding-catalog.json').is_file() else Path(__file__).resolve().parents[2]/'tests/fixtures/f3'
impl=runpy.run_path(str(Path(__file__).with_name('constraint-v1-trie.py')))
class ByteTokenizer:
    def __call__(self,text,**kw):return {'input_ids':[b+3 for b in text.encode()]}
    def decode(self,ids,**kw):return bytes(i-3 for i in ids if i!=2).decode()
class Tests(unittest.TestCase):
    def setUp(self):
        self.catalog=json.loads((FIXTURES/'grounding-catalog.json').read_text())
        c=self.catalog['claims'][0];s=c['support_alternatives'][0][0]
        self.evidence=[{'chunk_id':'00000000-0000-0000-0000-000000000001','use_case_id':c['use_case_id'],**{k:s[k] for k in ('source_id','revision','content_sha256','start','end')},'text':s['quote']}]
        self.snapshot={'use_case_id':'f2-synthetic','registry_fingerprint':'a'*64,'represented_sources':[{k:s[k] for k in ('source_id','revision','content_sha256')} for s in self.catalog['source_rules'] if s['use_case_id']=='f2-synthetic']}
        self.context={'question':'What is the return policy?','rules':[{'claim_id':c['claim_id'],'text':c['text']}],'evidence':self.evidence}
        self.binding={'catalog':self.catalog,'scope':'f2-synthetic','snapshot':self.snapshot,'context':self.context}
    def compile(self):return impl['compile_choices'](self.context,self.binding,ByteTokenizer(),2)
    def test_two_real_alternatives(self):
        t=self.compile();self.assertEqual(len(t.texts),2);self.assertEqual({json.loads(s)['status'] for s in t.texts},{'answered','insufficient_evidence'})
    def test_premature_eos_rejected(self):
        t=self.compile();self.assertNotIn(2,t.allowed([]));self.assertRaises(ValueError,t.allowed,[2])
    def test_fabricated_id_not_a_path(self):
        t=self.compile();bad=t.texts[0].replace(self.evidence[0]['chunk_id'],'00000000-0000-0000-0000-000000000999');prefix=[]
        rejected=False
        for token in ByteTokenizer()(bad)['input_ids']+[2]:
            if token not in t.allowed(prefix):rejected=True;break
            prefix.append(token)
        self.assertTrue(rejected)
    def test_unsupported_quote_rejected(self):
        self.evidence[0]['text']='x'*len(self.evidence[0]['text']);self.assertRaises(ValueError,self.compile)
    def test_stale_revision_rejected(self):
        self.evidence[0]['revision']='v2';self.assertRaises(ValueError,self.compile)
    def test_wrong_scope_rejected(self):
        self.evidence[0]['use_case_id']='f2-neighbor';self.assertRaises(ValueError,self.compile)
    def test_ambiguous_support_rejected(self):
        self.evidence.append({**self.evidence[0],'chunk_id':'00000000-0000-0000-0000-000000000002'});self.assertRaises(ValueError,self.compile)
    def test_unreviewed_rule_rejected(self):
        self.context['rules'][0]['text']='Invented rule';self.assertRaises(ValueError,self.compile)
    def test_terminal_eos_and_prompt_slicing(self):
        t=self.compile();ids=ByteTokenizer()(t.texts[0])['input_ids'];self.assertEqual(t.allowed(ids),[2]);self.assertEqual(t.callback(3)(0,[200,200,200]+ids),[2]);self.assertRaises(ValueError,t.allowed,ids+[2])
    def test_existing_validator_fabricated_id(self):
        value={'status':'answered','claims':[{'claim_id':'returns','text':self.catalog['claims'][0]['text'],'chunk_ids':['00000000-0000-0000-0000-000000000999']}],'reason':None}
        with self.assertRaisesRegex(ValueError,'invalid_citation'):validate_claims(value,self.catalog['claims'],self.evidence)
    def test_existing_validator_unsupported_claim(self):
        value={'status':'answered','claims':[{'claim_id':'returns','text':'Unlimited returns','chunk_ids':[self.evidence[0]['chunk_id']]}],'reason':None}
        with self.assertRaisesRegex(ValueError,'grounding_failed'):validate_claims(value,self.catalog['claims'],self.evidence)
    def test_existing_validator_valid_id_unrelated_text(self):
        value={'status':'answered','claims':[{'claim_id':'returns','text':self.catalog['claims'][0]['text'],'chunk_ids':[self.evidence[0]['chunk_id']]}],'reason':None}
        self.evidence[0]['text']='x'*len(self.evidence[0]['text'])
        with self.assertRaisesRegex(ValueError,'grounding_failed'):validate_claims(value,self.catalog['claims'],self.evidence)
    def test_missing_field_extra_text_and_source_wording_rejected(self):
        t=self.compile();good=json.loads(t.texts[0]);variants=[]
        bad=copy.deepcopy(good);del bad['claims'][0]['chunk_ids'];variants.append(json.dumps(bad))
        bad=copy.deepcopy(good);bad['claims'][0]['text']=self.evidence[0]['text'];variants.append(json.dumps(bad))
        variants.append(t.texts[0]+' trailing')
        for text in variants:
            prefix=[];rejected=False
            for token in ByteTokenizer()(text)['input_ids']+[2]:
                if token not in t.allowed(prefix):rejected=True;break
                prefix.append(token)
            self.assertTrue(rejected)
    def test_large_path_rejected(self):
        self.assertRaises(ValueError,impl['Trie'],['x'*384],ByteTokenizer(),2)
    def test_binding_mismatch_rejected(self):
        self.binding=copy.deepcopy(self.binding);self.binding['context']['question']='Different question';self.assertRaises(ValueError,self.compile)
    def test_real_greedy_processor_masks_invalid_ids_and_eos(self):
        try:
            import torch
            from transformers.generation.logits_process import PrefixConstrainedLogitsProcessor
        except ImportError:self.skipTest('real Torch processor checked in existing offline Linux image')
        t=self.compile();allow=t.callback(2);ids=torch.tensor([[200,201]])
        scores=torch.zeros((1,259));scores[0,2]=100;scores[0,258]=99
        masked=PrefixConstrainedLogitsProcessor(allow,1)(ids,scores)
        self.assertEqual(torch.isfinite(masked).nonzero()[:,1].tolist(),t.allowed([]))
        self.assertNotEqual(masked.argmax(-1).item(),2)
        self.assertRaises(ValueError,PrefixConstrainedLogitsProcessor(allow,1),torch.tensor([[200,201,2]]),scores)
if __name__=='__main__':unittest.main()
