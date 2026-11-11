import math

# [PERF] Lazy-load CLIP tokenizer at first use instead of import time.
# The original version downloads/loads the tokenizer when the module is
# imported, which costs several seconds on startup and blocks everything.
# Tokenization results are cached: the original code re-tokenized every tag
# of every image on each construct_tag_infos() call (O(N*T) HF-tokenizer
# calls), which was the single biggest lag source of this app.

_tokenizer = None
_token_cache = {}
_CACHE_LIMIT = 200000


def _get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        from transformers import CLIPTokenizerFast
        _tokenizer = CLIPTokenizerFast.from_pretrained(
            "openai/clip-vit-large-patch14"
        )
    return _tokenizer


def tokenize(text: str):
    cached = _token_cache.get(text)
    if cached is not None:
        return cached
    try:
        tokens = _get_tokenizer().tokenize(text)
    except Exception:
        tokens = []
    result = (tokens, len(tokens))
    if len(_token_cache) < _CACHE_LIMIT:
        _token_cache[text] = result
    return result


def get_target_token_count(token_count: int):
    return (
        math.ceil(max(token_count, 1) / _get_tokenizer().max_len_single_sentence)
        * _get_tokenizer().max_len_single_sentence
    )
