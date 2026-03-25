import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

# 1. Load a pretrained Sentence Transformer model
class SimpleRAG:
    def __init__ (self,model_name:str="all-MiniLM-L6-v2"):

        self.encoder=SentenceTransformer(model_name)
        self.documents=[]
        self.embeddings=None
    
    def add_documents(self,docs:list[str]):
        self.documents.extend(docs)
        self.embeddings=self.encoder.encode(self.documents)

    def retrieve(self, query:str, top_k:int=3) ->list[tuple[str,float]]:
        if self.embeddings is None or len(self.documents)==0:
             
            return[]
        query_embedding= self.encoder.encode([query])[0]
        similarities=np.dot(self.embeddings,query_embedding)/(np.linalg.norm(self.embeddings,axis=1)*np.linalg.norm(query_embedding))
    
    
        top_indices=np.argsort(similarities)[::-1] [:top_k]
        result= [[self.documents[i], float(similarities[i])]for i in top_indices]
        return result

if __name__=="__main__":
   rag=SimpleRAG()
   documents=[
       "Python is a programming language",
       "It also helps in machine learning concepts",
       "It also used in creating artificial intelligence projects"
   ]
   print("Adding documents:")
   rag.add_documents(documents)
   query=input("Enter your query:")
  
   print(f"\nquery:{query}")
   print("\n top results:")
   results=rag.retrieve(query,top_k=3)
   for doc,score in results:
       print(f"[{score:4f}] {doc}")




