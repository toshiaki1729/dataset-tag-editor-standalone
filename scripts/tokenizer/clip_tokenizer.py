import math
from transformers import CLIPTokenizerFast

tokenizer: CLIPTokenizerFast = CLIPTokenizerFast.from_pretrained(
    "openai/clip-vit-large-patch14"
)


def tokenize(text: str):
    try:
        tokens = tokenizer.tokenize(text)
    except:
        pass
    token_count = len(tokens)
    return tokens, token_count


def get_target_token_count(token_count: int):
    return (
        math.ceil(max(token_count, 1) / tokenizer.max_len_single_sentence)
        * tokenizer.max_len_single_sentence
    )
