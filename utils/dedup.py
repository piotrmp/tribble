# Adapted from https://github.com/facebookresearch/stopes/blob/main/stopes/pipelines/filtering/filters/dedup.py
import pandas as pd
import xxhash
from collections import Counter
from typing import Dict, Set, Tuple
import re
import unicodedata


def normalize_for_dedup(text: str) -> str:
    """
    Normalize text for deduplication purposes.

    This function performs the following operations:
    1. Strips leading and trailing whitespace
    2. Converts to lowercase
    3. Removes accents and diacritical marks
    4. Replaces digits with '0'
    5. Removes punctuation and control characters
    6. Removes tabs and excessive whitespace

    Args:
    text (str): The input text to normalize

    Returns:
    str: The normalized text
    """
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove accents and diacritical marks
    text = ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn')

    # Replace digits with '0'
    text = re.sub(r'\d', '0', text)

    # Remove punctuation and control characters
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)

    # Remove tabs and normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def compute_hashes(src: str, tgt: str, dedup_pairs: bool) -> Tuple[int, int, int]:
    normalized_src = normalize_for_dedup(src)
    normalized_tgt = normalize_for_dedup(tgt) if tgt else ""

    src_hash = xxhash.xxh3_64_intdigest(normalized_src)
    tgt_hash = xxhash.xxh3_64_intdigest(normalized_tgt) if tgt else None

    pair_hash = None
    if dedup_pairs:
        pair_text = f"{normalized_src}\t{normalized_tgt}" if tgt else normalized_src
        pair_hash = xxhash.xxh3_64_intdigest(pair_text)

    return src_hash, tgt_hash, pair_hash


def dedup_filter(
        df: pd.DataFrame,
        dedup_pairs: bool = True,
        max_source_dedup: int = None,
        max_target_dedup: int = None
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    seen_pair_hashes: Set[int] = set()
    source_dup_counts: Dict[int, int] = Counter()
    target_dup_counts: Dict[int, int] = Counter()
    counts = {"pair_dedup": 0, "source_dedup": 0, "target_dedup": 0}

    def filter_row(row):
        src_hash, tgt_hash, pair_hash = compute_hashes(row['src_text'], row['tgt_text'], dedup_pairs)

        if dedup_pairs and pair_hash in seen_pair_hashes:
            counts["pair_dedup"] += 1
            return False
        if dedup_pairs:
            seen_pair_hashes.add(pair_hash)

        if max_target_dedup is not None and tgt_hash:
            if target_dup_counts[tgt_hash] >= max_target_dedup:
                counts["target_dedup"] += 1
                return False
            target_dup_counts[tgt_hash] += 1

        if max_source_dedup is not None:
            if source_dup_counts[src_hash] >= max_source_dedup:
                counts["source_dedup"] += 1
                return False
            source_dup_counts[src_hash] += 1

        return True

    filtered_df = df[df.apply(filter_row, axis=1)]
    return filtered_df, counts


if __name__ == "__main__":
    data = {
        'src_text': ["Hello, world!", "Hello, World!", "World 123", "World 456", "Hello world!!!", "Hello world???"],
        'tgt_text': ["Bonjour, le monde!", "Salut, le Monde!", "Monde 123", "Monde 456", "Bonjour le monde!!!",
                     "Bonjour le monde???"]
    }
    df = pd.DataFrame(data)

    print("Original DataFrame:")
    print(df)

    filtered_df, dedup_counts = dedup_filter(
        df,
        dedup_pairs=True,
        max_source_dedup=2,
        max_target_dedup=1
    )

    print("\nFiltered DataFrame:")
    print(filtered_df)

    print("\nDeduplication counts:")
    for key, value in dedup_counts.items():
        print(f"{key}: {value}")