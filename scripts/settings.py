import json
from typing import NamedTuple
from utilities import base_dir_path

SETTING_PATH = base_dir_path() / "settings.json"

class Settings(NamedTuple):
    allowed_paths: str = ''
    use_temp_files: bool = False
    temp_directory: str = ''
    cleanup_tmpdir: bool = True
    image_columns: int = 6
    max_resolution: int = 0
    filename_word_regex: str = ""
    filename_join_string: str = " "
    tagger_use_spaces: bool = True
    interrogator_use_cpu: bool = False
    interrogator_keep_in_memory: bool = False
    interrogator_max_length: int = 30
    interrogator_model_dir: str = ""
    tagger_use_rating: bool = False
    num_cpu_worker: int = -1
    # [PERF] gallery pagination: max number of images rendered per page (0 = all)
    gallery_page_size: int = 200
    # Smart tag deduplication: optional LLM backend (OpenAI-compatible or Anthropic)
    dedup_llm_api_type: str = "openai"
    dedup_llm_base_url: str = ""
    dedup_llm_model: str = ""
    dedup_llm_api_key: str = ""
    dedup_rules_file: str = ""
    batch_size_vit:int = 4
    batch_size_vit_large:int = 4
    batch_size_convnext:int = 4
    batch_size_swinv2:int = 4
    batch_size_eva02_large:int = 4


DEFAULT = Settings()
current = Settings()


NAMES = list(Settings.__annotations__.keys())

DESCRIPTIONS = {
    "allowed_paths": "Path whitelist to show images in gallery (for local use). Split paths by comma and space (, )",
    "use_temp_files": "Force using temporary file to show images on gallery",
    "temp_directory": "Directory to save temporary files",
    "cleanup_tmpdir": "Cleanup temporary files on startup",
    "image_columns": "Column number of image galleries",
    "max_resolution": "Maximum resolution of gallery thumbnails (0 to disable)",
    "filename_word_regex": "regex to read caption from filename",
    "filename_join_string" : "Characters to insert between the words which matches with regex",
    "tagger_use_spaces": "Replace underbar (_) in tags with whitespace ( )",
    "interrogator_use_cpu": "Use CPU to interrogate",
    "interrogator_keep_in_memory": "Keep interroagor in VRAM",
    "interrogator_max_length": "Maximum text length for interrogator (for GIT only)",
    "interrogator_model_dir": "Path to directory for downloaded interrogator models",
    "tagger_use_rating": "Use Rating tags when using Tagger",
    "num_cpu_worker": "Number of CPU workers when loading or preprocessing images (set -1 to auto)",
    "gallery_page_size": "[PERF] Max images shown per gallery page (0 to show all; smaller = snappier UI)",
    "dedup_llm_api_type": "Smart Dedup LLM API type: 'openai' (OpenAI-compatible: llama.cpp / Ollama / vLLM / OpenAI) or 'anthropic'",
    "dedup_llm_base_url": "Smart Dedup LLM base URL, e.g. http://127.0.0.1:8080 or https://api.openai.com (with or without /v1)",
    "dedup_llm_model": "Smart Dedup LLM model name, e.g. gpt-4o-mini or a local model id",
    "dedup_llm_api_key": "Smart Dedup LLM API key (leave empty for local servers without auth)",
    "dedup_rules_file": "Smart Dedup custom rules JSON file (optional; extends the built-in implication table)",
    "batch_size_vit": "Inference batch size for ViT taggers",
    "batch_size_vit_large": "Inference batch size for ViT large taggers",
    "batch_size_convnext": "Inference batch size for ConvNeXt taggers",
    "batch_size_swinv2": "Inference batch size for SwinV2 taggers",
    "batch_size_eva02_large": "Inference batch size for EVA-02 large taggers",
}



def save():
    SETTING_PATH.write_text(json.dumps(current._asdict()), "utf8")


def load():
    global current
    if SETTING_PATH.is_file():
        settings = DEFAULT._asdict() | json.loads(SETTING_PATH.read_text("utf8"))
    else:
        settings = DEFAULT._asdict()
    settings = {key:value for key,value in settings.items() if key in DEFAULT._asdict()}
    current = Settings(**settings)


def restore_defaults():
    global current
    current = Settings()