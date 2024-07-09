# Adapted from https://github.com/facebookresearch/stopes/blob/main/stopes/pipelines/filtering/filters/length.py
from typing import Dict, List


def compute_length(text: str, factor: float = 1.0) -> int:
    return max(1, len(text) * factor)


def compute_ratio(src_len: int, tgt_len: int) -> float:
    return max(src_len / tgt_len, tgt_len / src_len)


def ngrams(string: str, order: int) -> List[str]:
    string = string.strip().replace(" ", "")
    return [string[i:i + order] for i in range(len(string) - order + 1)]


def compute_unique_ratio(text: str, src_factor: float) -> float:
    order = min(1, 6 * src_factor)
    if order != int(order):
        raise ValueError(f"Length factor {src_factor} results in non-integer ngram order")
    ngrms = ngrams(text, order=int(order))
    return len(set(ngrms)) / len(ngrms) if ngrms else 0

def filter_length(
    src_len: int,
    tgt_len: int,
    len_ratio: float,
    unique_ratio: float,
    min_len: int = 5,
    max_len: int = 1050,
    max_len_ratio: float = 9.0,
    min_src_unique_ratio: float = 0.5
) -> bool:
    if src_len < min_len or tgt_len < min_len:
        return False
    if src_len > max_len or tgt_len > max_len:
        return False
    if len_ratio > max_len_ratio:
        return False
    if unique_ratio < min_src_unique_ratio:
        return False
    return True
