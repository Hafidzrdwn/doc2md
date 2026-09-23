from core.chunker import count_tokens, chunk_by_tokens

def test_count_tokens_empty():
    assert count_tokens("") == 0

def test_count_tokens_valid():
    text = "Halo dunia, ini pengujian tokenisasi AI."
    tokens = count_tokens(text)
    assert tokens > 0

def test_chunk_by_tokens_under_limit():
    text = "Kalimat singkat."
    chunks = chunk_by_tokens(text, max_tokens=100)
    assert len(chunks) == 1
    assert chunks[0] == text

def test_chunk_by_tokens_over_limit():
    # Construct a large text with repeating words
    text = "Kata pengujian yang diulang berkali-kali. " * 200
    total_tokens = count_tokens(text)
    max_chunk = 50
    chunks = chunk_by_tokens(text, max_tokens=max_chunk)

    assert len(chunks) > 1
    for chunk in chunks:
        assert count_tokens(chunk) <= max_chunk
