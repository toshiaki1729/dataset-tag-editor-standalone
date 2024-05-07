from PIL import Image
from typing import Optional, Generator, Any
from datasets import Dataset

import settings

# Custom tagger classes have to inherit from this class
class Tagger:
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.stop()
        pass

    def start(self):
        pass

    def stop(self):
        pass

    # predict tags of one image
    def predict(self, image: Image.Image, threshold: Optional[float]) -> list[str]:
        raise NotImplementedError()
    
    # Please implement if you want to use more efficient data loading system
    # None input will come to check if this function is implemented
    def predict_pipe(self, data: list[Image.Image], threshold: Optional[float]) -> Generator[list[str], Any, None]:
        raise NotImplementedError()

    def name(self):
        raise NotImplementedError()


def get_replaced_tag(tag: str):
    use_spaces = settings.current.tagger_use_spaces
    if use_spaces:
        tag = tag.replace("_", " ")
    return tag


def get_arranged_tags(probs: dict[str, float]):
    return [tag for tag, _ in sorted(probs.items(), key=lambda x: -x[1])]
