from __future__ import annotations
from typing import TYPE_CHECKING, Callable

import gradio as gr

import settings
from .ui_common import *
from .uibase import UIBase

if TYPE_CHECKING:
    from .ui_classes import *
Filter = dte_module.filters.Filter


class DatasetGalleryUI(UIBase):
    def __init__(self):
        self.selected_path = ""
        self.selected_index = -1
        # [PERF] gallery pagination (0-based)
        self.page = 0

    def create_ui(self, image_columns, get_filters: Callable[[], list[Filter]]):
        with gr.Row():
            # [PERF] pagination controls
            self.btn_prev_page = gr.Button(value="← Prev Page", scale=1)
            self.txt_page_info = gr.Markdown(value="Page 1/1")
            self.btn_next_page = gr.Button(value="Next Page →", scale=1)
        self.gl_dataset_images = gr.Gallery(
            label="Dataset Images", elem_id="dataset_gallery", columns=image_columns)
        self.get_filters = get_filters

    def page_size(self) -> int:
        return max(0, int(settings.current.gallery_page_size))

    def apply_pagination(self, imgs: list):
        """[PERF] Slice the filtered image list to the current page.
        Returns (page_imgs, page, total_pages)."""
        ps = self.page_size()
        total = len(imgs)
        if ps <= 0:
            self.page = 0
            return imgs, 0, 1
        total_pages = max(1, (total + ps - 1) // ps)
        self.page = max(0, min(self.page, total_pages - 1))
        start = self.page * ps
        return imgs[start:start + ps], self.page, total_pages

    def reset_page(self):
        self.page = 0

    def set_callbacks(
        self,
        gallery_state: GalleryStateUI,
        update_gallery: Callable[[], list],
        o_update_gallery: list,
    ):
        def gl_dataset_images_on_change(select_data: gr.SelectData):
            if select_data.selected:
                imgs = dte_instance.get_filtered_imgpaths(self.get_filters())
                # [PERF] map gallery index back to the global filtered list
                idx = select_data.index + self.page * self.page_size()
                self.selected_index = idx if 0 <= idx < len(imgs) else -1
                self.selected_path = imgs[self.selected_index] if self.selected_index >= 0 else ""
            else:
                self.selected_index = -1
                self.selected_path = ""
            gallery_state.register_value("Selected Image", self.selected_path)
        
        self.gl_dataset_images.select(gl_dataset_images_on_change)

        def go_prev_page():
            self.page -= 1
            return update_gallery()

        def go_next_page():
            self.page += 1
            return update_gallery()

        self.btn_prev_page.click(fn=go_prev_page, outputs=o_update_gallery)
        self.btn_next_page.click(fn=go_next_page, outputs=o_update_gallery)
