import os
import sys
from typing import List
import tiktoken

_encoder = None

def get_encoder() -> tiktoken.Encoding:
    """Retrieve or initialize the cl100k_base tokenizer encoder."""
    global _encoder
    if _encoder is None:
        if getattr(sys, 'frozen', False):
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            tiktoken_cache = os.path.join(base_dir, "tiktoken_cache")
            if os.path.exists(tiktoken_cache):
                os.environ["TIKTOKEN_CACHE_DIR"] = str(tiktoken_cache)
        _encoder = tiktoken.get_encoding("cl100k_base")
    return _encoder

def count_tokens(text: str) -> int:
    """Calculate the total number of tokens for a given text."""
    if not text:
        return 0
    return len(get_encoder().encode(text))

def chunk_by_tokens(text: str, max_tokens: int = 15000) -> List[str]:
    """Split text into chunks that do not exceed max_tokens."""
    if not text:
        return []
    
    enc = get_encoder()
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:
        return [text]

    chunks = []
    for i in range(0, len(tokens), max_tokens):
        slice_tokens = tokens[i:i + max_tokens]
        chunks.append(enc.decode(slice_tokens))
    return chunks
