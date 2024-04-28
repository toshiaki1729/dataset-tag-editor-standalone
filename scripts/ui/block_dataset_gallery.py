from __future__ import annotations
from typing import TYPE_CHECKING, Callable

import gradio as gr

from .ui_common import *
from .uibase import UIBase

if TYPE_CHECKING:
    from .ui_classes import *
Filter = dte_module.filters.Filter


class DatasetGalleryUI(UIBase):
    def __init__(self):
        self.selected_path = ""
        self.selected_index = -1

    def create_ui(self, image_columns, get_filters: Callable[[], list[Filter]]):
        self.gl_dataset_images = gr.Gallery(
            label="Dataset Images", elem_id="dataset_gallery", columns=image_columns)
        self.get_filters = get_filters

    def set_callbacks(
        self,
        gallery_state: GalleryStateUI
    ):
        def gl_dataset_images_on_change(select_data: gr.SelectData):
            if select_data.selected:
                imgs = dte_instance.get_filtered_imgpaths(self.get_filters())
                self.selected_index = select_data.index
                self.selected_path = imgs[self.selected_index]
            gallery_state.register_value("Selected Image", self.selected_path)
        
        self.gl_dataset_images.select(gl_dataset_images_on_change)

    