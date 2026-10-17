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


def test_chunk_by_tokens_paragraph_boundary():
    para1 = "# Bab 1 Pendahuluan\n\nIni adalah paragraf pertama yang menjelaskan latar belakang penelitian secara lengkap."
    para2 = "## Bab 2 Tinjauan Pustaka\n\nIni adalah paragraf kedua yang menguraikan teori dasar dan metodologi."
    text = f"{para1}\n\n{para2}"
    
    tokens1 = count_tokens(para1 + "\n\n")
    # Split with max_tokens slightly larger than para1 but smaller than total
    chunks = chunk_by_tokens(text, max_tokens=tokens1 + 5)
    assert len(chunks) == 2
    assert "Bab 1 Pendahuluan" in chunks[0]
    assert "Bab 2 Tinjauan Pustaka" in chunks[1]

