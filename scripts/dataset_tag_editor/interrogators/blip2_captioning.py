from transformers import Blip2Processor, Blip2ForConditionalGeneration

import devices, settings, utilities
from paths import paths


class BLIP2Captioning:
    def __init__(self, model_repo: str):
        self.MODEL_REPO = model_repo
        self.processor: Blip2Processor = None
        self.model: Blip2ForConditionalGeneration = None

    def load(self):
        if self.model is None or self.processor is None:
            self.processor = Blip2Processor.from_pretrained(
                self.MODEL_REPO, cache_dir=paths.models_path / "aesthetic"
            )
            self.model = Blip2ForConditionalGeneration.from_pretrained(
                self.MODEL_REPO, cache_dir=paths.models_path / "aesthetic"
            ).to(devices.device)

    def unload(self):
        if not settings.current.interrogator_keep_in_memory:
            self.model = None
            self.processor = None
            devices.torch_gc()

    def apply(self, image):
        if self.model is None or self.processor is None:
            return ""
        inputs = self.processor(images=image, return_tensors="pt").to(devices.device)
        ids = self.model.generate(**inputs)
        return self.processor.batch_decode(ids, skip_special_tokens=True)
