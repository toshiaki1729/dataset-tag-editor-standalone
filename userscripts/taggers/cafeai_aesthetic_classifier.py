from PIL import Image
import math
from datasets import Dataset

from transformers import pipeline
import devices, settings
from paths import paths
from tagger import Tagger

# brought and modified from https://huggingface.co/spaces/cafeai/cafe_aesthetic_demo/blob/main/app.py

BATCH_SIZE = 8

class CafeAIAesthetic(Tagger):
    def load(self):
        self.pipe_aesthetic = pipeline("image-classification", "cafeai/cafe_aesthetic", device=devices.device, batch_size=BATCH_SIZE)
    
    def unload(self):
        if not settings.current.interrogator_keep_in_memory:
            self.pipe_aesthetic = None
            devices.torch_gc()

    def start(self):
        self.load()
        return self

    def stop(self):
        self.unload()

    def _get_score(self, data):
        final = {}
        for d in data:
            final[d["label"]] = d["score"]
        nae = final['not_aesthetic']
        ae = final['aesthetic']
        return [f"score_{math.floor((ae + (1 - nae))/2 * 10)}"]

    def predict(self, image: Image.Image, threshold=None):
        data = self.pipe_aesthetic(image, top_k=2)
        return self._get_score(data)
    
    def predict_pipe(self, data: list[Image.Image], threshold=None):
        if data is None:
            return
        for out in self.pipe_aesthetic(data):
            yield self._get_score(out)

    def name(self):
        return "cafeai aesthetic classifier"