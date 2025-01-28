import math
from transformers import CLIPTokenizerFast

_tokenizer: CLIPTokenizerFast = None

def init_tokenizer():
    global _tokenizer
    _tokenizer = CLIPTokenizerFast.from_pretrained("openai/clip-vit-base-patch32")

def get_tokenizer():
    if _tokenizer is None:
        init_tokenizer()
    return _tokenizer

def tokenize(text: str):
    try:
        tokens = get_tokenizer().tokenize(text)
    except:
        pass
    token_count = len(tokens)
    return tokens, token_count


def get_target_token_count(token_count: int):
    tokenizer = get_tokenizer()
    return (
        math.ceil(max(token_count, 1) / tokenizer.max_len_single_sentence)
        * tokenizer.max_len_single_sentence
    )
