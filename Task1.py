import json
import time
import re
from typing import Dict, Callable, Tuple, Type
def extract_text_from_pdf(pdf_path: str)-> str:
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise ImportError("Missing dependency. Install ") from e    
    reader=PdfReader(pdf_path)
    parts=[]
    for page in reader.pages:
        page_text= page.extract_text() or ""
    
    return "\n".join(parts)   
def truncate_to_token_limit(text: str,max_tokens:int=800)-> str:
    tokens=text.split()
    if len(tokens)<= max_tokens:
        return text
    return " ".join(tokens[:max_tokens])

def retry(
        func: Callable[[], str],
        retries:int=1,
        delay_seconds:float=0.5,
        exceptions: Tuple[Type[BaseException], ...]=(Exception,),)->callable[[], str]:
        def wrapped()->str:
             last_err=None
             for attempt in range(retries+1):
                  try:
                       return func()
                  except exceptions:
                       if attempt==retries:
                            raise
                       time.sleep(delay_seconds)
             raise RuntimeError("unreachable")
        return wrapped
FLAG_PATTERNS=[
     ("self_harm", re.compile(r"\b(suicide|self[-]harm|kill myself)\b, re.IGNORECASE"))

]
def moderate_text(text:str)-> Dict[str, str]:
     for category, pat in FLAG_PATTERNS:
          if pat.search(text):
               return {"allowed": False, "flag":category}
     return {"allowed": True, "flag":""}

def run_pipeline(pdf_path:str)->Dict:
     text= extract_text_from_pdf(pdf_path)
     if not text or not text.strip():
          return {"allowed": False, "flag":"empty_pdf"}
     text=truncate_to_token_limit(text, max_tokens=800)
     decision=moderate_text(text)
     if not decision["allowed"]:
          return {"allowed":False,"flag":decision["flag"]}
     
if __name__=="__main__":
     import sys
     if len(sys.argv)!=2:
          print("usage: python one-file_pipeline.py <apth_to_pdf>")
          raise SystemExit(1)  
     result= run_pipeline(sys.argv[1])
     print(json.dumps(result, ensure_ascii=False, indent=2)) 
                              
                       