from gradio.components.gallery import Gallery
from pathlib import Path
from typing import Any, Callable, Literal
import random
import string
import numpy as np
from PIL import Image as _Image  # using _ to minimize namespace pollution
from gradio import utils
import tqdm
import logger

def pil_to_temp_file(self: Gallery, img: _Image.Image, dir: str, format="png") -> str:
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    temp_dir = Path(dir) / "tag-editor-images"
    temp_dir.mkdir(exist_ok=True, parents=True)
    filename = str(temp_dir / f"{random_string}.{format}")
    img.save(filename)
    return filename


def postprocess(
    self: Gallery,
    y: list[np.ndarray | _Image.Image | str]
    | list[tuple[np.ndarray | _Image.Image | str, str]]
    | None,
) -> list[str]:
    """
    Parameters:
        y: list of images, or list of (image, caption) tuples
    Returns:
        list of string file paths to images in temp directory
    """
    if y is None:
        return []
    output = []
    logger.write("handle postprocess, save images to temp dir if use temp files. If this is slow, try to set Maximum resolution to 0 in settings to disable this.")
    for img in tqdm.tqdm(y):
        caption = None
        if isinstance(img, (tuple, list)):
            img, caption = img
        if isinstance(img, np.ndarray):
            file = self.img_array_to_temp_file(img, dir=self.DEFAULT_TEMP_DIR)
            file_path = str(utils.abspath(file))
            self.temp_files.add(file_path)
        elif isinstance(img, _Image.Image):
            file = self.pil_to_temp_file(img, dir=self.DEFAULT_TEMP_DIR)
            file_path = str(utils.abspath(file))
            self.temp_files.add(file_path)
        elif isinstance(img, (str, Path)):
            if utils.validate_url(img):
                file_path = img
            else:
                # file_path = self.make_temp_copy_if_needed(img)
                file_path = img
                self.temp_files.add(file_path)
        else:
            raise ValueError(f"Cannot process type as image: {type(img)}")

        if caption is not None:
            output.append(
                [{"name": file_path, "data": None, "is_file": True}, caption]
            )
        else:
            output.append({"name": file_path, "data": None, "is_file": True})

    return output

Gallery.postprocess = postprocess
# Gallery.pil_to_temp_file = pil_to_temp_file