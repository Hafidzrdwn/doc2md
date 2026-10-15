"""
Visual Document Diff Viewer Engine for Doc2MD.
Computes side-by-side and unified differences between two Markdown documents,
including token and character delta metrics.
"""

import difflib
from typing import Dict, List, Optional, Any
from core.chunker import count_tokens


def compute_document_diff(
    text_a: str,
    text_b: str,
    title_a: str = "Dokumen A (Versi Awal)",
    title_b: str = "Dokumen B (Versi Revisi)"
) -> Dict[str, Any]:
    """
    Compares two Markdown documents and generates structured diff output
    formatted for side-by-side and unified/inline visual rendering.
    """
    raw_a = text_a or ""
    raw_b = text_b or ""

    lines_a = raw_a.splitlines()
    lines_b = raw_b.splitlines()

    tokens_a = count_tokens(raw_a)
    tokens_b = count_tokens(raw_b)
    delta_tokens = tokens_b - tokens_a
    delta_chars = len(raw_b) - len(raw_a)

    matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
    similarity_ratio = round(matcher.ratio() * 100, 1)

    side_by_side: List[Dict[str, Any]] = []
    unified: List[Dict[str, Any]] = []

    added_count = 0
    removed_count = 0
    modified_count = 0
    unchanged_count = 0

    line_num_a = 1
    line_num_b = 1

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for a_idx, b_idx in zip(range(i1, i2), range(j1, j2)):
                la = lines_a[a_idx]
                lb = lines_b[b_idx]
                side_by_side.append({
                    "type": "equal",
                    "left": {"num": line_num_a, "text": la},
                    "right": {"num": line_num_b, "text": lb}
                })
                unified.append({
                    "type": "equal",
                    "text": la,
                    "left_num": line_num_a,
                    "right_num": line_num_b
                })
                line_num_a += 1
                line_num_b += 1
                unchanged_count += 1

        elif tag == "replace":
            len_a = i2 - i1
            len_b = j2 - j1
            max_len = max(len_a, len_b)
            modified_count += max_len

            start_num_a = line_num_a
            start_num_b = line_num_b

            for step in range(max_len):
                left_entry = None
                right_entry = None

                if step < len_a:
                    left_entry = {"num": start_num_a + step, "text": lines_a[i1 + step]}
                if step < len_b:
                    right_entry = {"num": start_num_b + step, "text": lines_b[j1 + step]}

                side_by_side.append({
                    "type": "replace",
                    "left": left_entry,
                    "right": right_entry
                })

            for step in range(len_a):
                unified.append({
                    "type": "delete",
                    "text": lines_a[i1 + step],
                    "left_num": line_num_a,
                    "right_num": None
                })
                line_num_a += 1
                removed_count += 1

            for step in range(len_b):
                unified.append({
                    "type": "insert",
                    "text": lines_b[j1 + step],
                    "left_num": None,
                    "right_num": line_num_b
                })
                line_num_b += 1
                added_count += 1

        elif tag == "delete":
            for step in range(i2 - i1):
                side_by_side.append({
                    "type": "delete",
                    "left": {"num": line_num_a, "text": lines_a[i1 + step]},
                    "right": None
                })
                unified.append({
                    "type": "delete",
                    "text": lines_a[i1 + step],
                    "left_num": line_num_a,
                    "right_num": None
                })
                line_num_a += 1
                removed_count += 1

        elif tag == "insert":
            for step in range(j2 - j1):
                side_by_side.append({
                    "type": "insert",
                    "left": None,
                    "right": {"num": line_num_b, "text": lines_b[j1 + step]}
                })
                unified.append({
                    "type": "insert",
                    "text": lines_b[j1 + step],
                    "left_num": None,
                    "right_num": line_num_b
                })
                line_num_b += 1
                added_count += 1

    return {
        "title_a": title_a,
        "title_b": title_b,
        "similarity_ratio": similarity_ratio,
        "stats": {
            "tokens_a": tokens_a,
            "tokens_b": tokens_b,
            "delta_tokens": delta_tokens,
            "chars_a": len(raw_a),
            "chars_b": len(raw_b),
            "delta_chars": delta_chars,
            "added_lines": added_count,
            "removed_lines": removed_count,
            "modified_lines": modified_count,
            "unchanged_lines": unchanged_count,
            "total_lines_a": len(lines_a),
            "total_lines_b": len(lines_b),
        },
        "side_by_side": side_by_side,
        "unified": unified
    }
