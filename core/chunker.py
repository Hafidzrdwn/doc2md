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

import re

def chunk_by_tokens(text: str, max_tokens: int = 15000) -> List[str]:
    """
    Split text into chunks that do not exceed max_tokens,
    intelligently splitting along paragraph, sentence, and word boundaries
    to prevent truncated sentences and sliced words.
    """
    if not text:
        return []

    enc = get_encoder()
    tokens = enc.encode(text)
    if len(tokens) <= max_tokens:
        return [text]

    paragraphs = text.split("\n\n")
    chunks = []
    curr_chunk = []
    curr_tokens = 0

    def add_line_segment(line: str):
        nonlocal curr_chunk, curr_tokens
        # Try splitting by sentence if line is long
        sentences = re.split(r'(?<=[.!?])\s+', line)
        if len(sentences) <= 1:
            # Try splitting by words
            words = line.split(" ")
            word_buf = []
            word_tokens = 0
            for w in words:
                wt = len(enc.encode(w + " "))
                if word_tokens + wt <= max_tokens:
                    word_buf.append(w)
                    word_tokens += wt
                else:
                    if word_buf:
                        chunks.append(" ".join(word_buf).strip())
                        word_buf = []
                        word_tokens = 0
                    if wt > max_tokens:
                        # Extreme edge case: a single word longer than max_tokens
                        chunks.append(w)
                    else:
                        word_buf.append(w)
                        word_tokens += wt
            if word_buf:
                chunks.append(" ".join(word_buf).strip())
        else:
            sent_buf = []
            sent_tokens = 0
            for s in sentences:
                st = len(enc.encode(s + " "))
                if sent_tokens + st <= max_tokens:
                    sent_buf.append(s)
                    sent_tokens += st
                else:
                    if sent_buf:
                        chunks.append(" ".join(sent_buf).strip())
                        sent_buf = []
                        sent_tokens = 0
                    if st > max_tokens:
                        add_line_segment(s)
                    else:
                        sent_buf.append(s)
                        sent_tokens += st
            if sent_buf:
                chunks.append(" ".join(sent_buf).strip())

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

            # If paragraph exceeds max_tokens, split by lines
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
                        if lt > max_tokens:
                            add_line_segment(line)
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

    return [c for c in chunks if c.strip()] if chunks else [text]

