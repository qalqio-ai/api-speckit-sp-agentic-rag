"""Deterministic query processor seam; never claims local model acceptance."""
from app.ingestion.embedding import validate_vectors
from app.ingestion.types import IngestionError


class QueryProcessor:
    mode='deterministic'
    def __init__(self,tokenizer,encoder,clock):
        self.tokenizer,self.encoder,self.clock=tokenizer,encoder,clock
    def encode(self,question,deadline,*,validate_only=False):
        if self.clock()>=deadline:raise IngestionError('deadline_exceeded')
        try:
            tokens=self.tokenizer(question,add_special_tokens=True,truncation=False)['input_ids']
            if len(tokens)>256:raise IngestionError('question_too_long')
            if self.clock()>=deadline:raise IngestionError('deadline_exceeded')
            if validate_only:return None
            vectors=self.encoder.encode([question],convert_to_numpy=True,show_progress_bar=False)
            vectors=vectors.tolist() if hasattr(vectors,'tolist') else vectors
            if len(vectors)!=1:raise IngestionError('embedding_failed')
            validate_vectors(vectors)
            if self.clock()>=deadline:raise IngestionError('deadline_exceeded')
            return vectors[0]
        except IngestionError:raise
        except Exception as error:raise IngestionError('embedding_failed') from error
