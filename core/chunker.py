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
    """
    Split text into chunks that do not exceed max_tokens,
    intelligently splitting along paragraph and line boundaries to prevent truncated sentences.
    """
    if not text:
        return []
    
    enc = get_encoder()
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:
        return [text]

    # Split by paragraphs
    paragraphs = text.split("\n\n")
    chunks = []
    curr_chunk = []
    curr_tokens = 0

    for para in paragraphs:
        para_tokens = len(enc.encode(para + "\n\n"))
        if curr_tokens + para_tokens <= max_tokens:
            curr_chunk.append(para)
            curr_tokens += para_tokens
        else:
            if curr_chunk:
                chunks.append("\n\n".join(curr_chunk).strip())
                curr_chunk = []
                curr_tokens = 0

            # If a single paragraph exceeds max_tokens on its own, split by lines
            if para_tokens > max_tokens:
                lines = para.split("\n")
                line_chunk = []
                line_tokens = 0
                for line in lines:
                    lt = len(enc.encode(line + "\n"))
                    if line_tokens + lt <= max_tokens:
                        line_chunk.append(line)
                        line_tokens += lt
                    else:
                        if line_chunk:
                            chunks.append("\n".join(line_chunk).strip())
                            line_chunk = []
                            line_tokens = 0
                        # If a single line still exceeds max_tokens, fallback to token slicing
                        if lt > max_tokens:
                            sub_tokens = enc.encode(line)
                            for i in range(0, len(sub_tokens), max_tokens):
                                chunks.append(enc.decode(sub_tokens[i:i + max_tokens]))
                        else:
                            line_chunk.append(line)
                            line_tokens += lt
                if line_chunk:
                    curr_chunk.append("\n".join(line_chunk))
                    curr_tokens += line_tokens
            else:
                curr_chunk.append(para)
                curr_tokens += para_tokens

    if curr_chunk:
        chunks.append("\n\n".join(curr_chunk).strip())

    return chunks if chunks else [text]

