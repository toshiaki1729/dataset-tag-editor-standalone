from typing import Callable
import gradio as gr

from .ui_common import *

filters = dte_module.filters
TagFilter = filters.TagFilter

SortBy = dte_instance.SortBy
SortOrder = dte_instance.SortOrder


class TagFilterUI:
    def __init__(self, tag_filter_mode=TagFilter.Mode.INCLUSIVE):
        self.logic = TagFilter.Logic.AND
        self.filter_word = ""
        self.sort_by = SortBy.ALPHA
        self.sort_order = SortOrder.ASC
        self.selected_tags = set()
        self.visible_tags = set()
        self.filter_mode = tag_filter_mode
        self.filter = TagFilter(logic=self.logic, mode=self.filter_mode)
        self.get_filters = lambda: []
        self.prefix = False
        self.suffix = False
        self.regex = False
        self.after_filter_update_callbacks = []

    def get_filter(self):
        return self.filter

    def create_ui(
        self,
        get_filters: Callable[[], list[filters.Filter]],
        logic=TagFilter.Logic.AND,
        sort_by=SortBy.ALPHA,
        sort_order=SortOrder.ASC,
        prefix=False,
        suffix=False,
        regex=False,
    ):
        self.get_filters = get_filters
        self.logic = logic
        self.filter = filters.TagFilter(logic=self.logic, mode=self.filter_mode)
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.prefix = prefix
        self.suffix = suffix
        self.regex = regex

        self.tb_search_tags = gr.Textbox(label="Search Tags", interactive=True)
        with gr.Row():
            self.cb_prefix = gr.Checkbox(
                label="Prefix", value=self.prefix, interactive=True
            )
            self.cb_suffix = gr.Checkbox(
                label="Suffix", value=self.suffix, interactive=True
            )
            self.cb_regex = gr.Checkbox(
                label="Use regex", value=self.regex, interactive=True
            )
        with gr.Row():
            self.rb_sort_by = gr.Radio(
                choices=[e.value for e in SortBy],
                value=sort_by,
                interactive=True,
                label="Sort by",
            )
            self.rb_sort_order = gr.Radio(
                choices=[e.value for e in SortOrder],
                value=sort_order,
                interactive=True,
                label="Sort Order",
            )
        v = (
            "AND"
            if self.logic == TagFilter.Logic.AND
            else "OR"
            if self.logic == TagFilter.Logic.OR
            else "NONE"
        )
        self.rb_logic = gr.Radio(
            choices=["AND", "OR", "NONE"],
            value=v,
            label="Filter Logic",
            interactive=True,
        )
        
        with gr.Row():
            self.btn_select_visibles = gr.Button(value="Select visible tags")
            self.btn_deselect_visibles = gr.Button(value="Deselect visible tags")
            
        self.cbg_tags = gr.CheckboxGroup(
            label="Filter Images by Tags", interactive=True
        )

    def after_filter_update(
        self, fn: Callable[[list], list], inputs=None, outputs=None, js=None
    ):
        self.after_filter_update_callbacks.append((fn, inputs, outputs, js))

    def set_callbacks(self):
        o_update = self.cbg_tags

        self.tb_search_tags.change(
            fn=self.tb_search_tags_changed,
            inputs=self.tb_search_tags
        ).then(
            fn=self.cbg_tags_update, outputs=o_update
        )
        self.cb_prefix.change(
            fn=self.cb_prefix_changed, inputs=self.cb_prefix, outputs=o_update
        )
        self.cb_suffix.change(
            fn=self.cb_suffix_changed, inputs=self.cb_suffix, outputs=o_update
        )
        self.cb_regex.change(
            fn=self.cb_regex_changed, inputs=self.cb_regex, outputs=o_update
        )
        self.rb_sort_by.change(
            fn=self.rd_sort_by_changed, inputs=self.rb_sort_by, outputs=o_update
        )
        self.rb_sort_order.change(
            fn=self.rd_sort_order_changed,
            inputs=self.rb_sort_order,
            outputs=o_update,
        )

        self.rb_logic.change(
            fn=self.rd_logic_changed, inputs=[self.rb_logic], outputs=o_update
        )
        for fn, inputs, outputs, js in self.after_filter_update_callbacks:
            self.rb_logic.change(fn=lambda:None).then(fn=fn, inputs=inputs, outputs=outputs, js=js)

        self.btn_select_visibles.click(
            fn=self.btn_select_visibles_clicked, outputs=o_update
        )
        self.btn_deselect_visibles.click(
            fn=self.btn_deselect_visibles_clicked,
            inputs=self.cbg_tags,
            outputs=o_update,
        )

        self.cbg_tags.change(
            fn=self.cbg_tags_changed, inputs=self.cbg_tags, outputs=o_update
        )
        for fn, inputs, outputs, js in self.after_filter_update_callbacks:
            self.cbg_tags.change(fn=lambda:None).then(fn=fn, inputs=inputs, outputs=outputs, js=js)

    def tb_search_tags_changed(self, tb_search_tags: str):
        self.filter_word = tb_search_tags

    def cb_prefix_changed(self, prefix: bool):
        self.prefix = prefix
        return self.cbg_tags_update()

    def cb_suffix_changed(self, suffix: bool):
        self.suffix = suffix
        return self.cbg_tags_update()

    def cb_regex_changed(self, use_regex: bool):
        self.regex = use_regex
        return self.cbg_tags_update()

    def rd_sort_by_changed(self, rb_sort_by: str):
        self.sort_by = rb_sort_by
        return self.cbg_tags_update()

    def rd_sort_order_changed(self, rd_sort_order: str):
        self.sort_order = rd_sort_order
        return self.cbg_tags_update()

    def rd_logic_changed(self, rd_logic: str):
        self.logic = (
            TagFilter.Logic.AND
            if rd_logic == "AND"
            else TagFilter.Logic.OR
            if rd_logic == "OR"
            else TagFilter.Logic.NONE
        )
        self.filter = TagFilter(self.selected_tags, self.logic, self.filter_mode)
        return self.cbg_tags_update()
    
    def btn_deselect_visibles_clicked(self, cbg_tags: list[str]):
        selected_tags = set(dte_instance.read_tags(cbg_tags))
        self.selected_tags -= selected_tags
        return self.cbg_tags_update()

    def btn_select_visibles_clicked(self):
        self.selected_tags |= self.visible_tags
        return self.cbg_tags_update()

    def cbg_tags_changed(self, cbg_tags: list[str]):
        selected_tags = dte_instance.cleanup_tagset(
            set(dte_instance.read_tags(cbg_tags))
        )
        invisible_selected_tags = self.filter.tags & (dte_instance.get_tag_set() - self.visible_tags)
        self.selected_tags = selected_tags | invisible_selected_tags
        return self.cbg_tags_update()

    def cbg_tags_update(self):
        self.selected_tags = dte_instance.cleanup_tagset(self.selected_tags)
        self.filter = TagFilter(self.selected_tags, self.logic, self.filter_mode)

        if self.filter_mode == TagFilter.Mode.INCLUSIVE:
            tags = dte_instance.get_filtered_tags(
                self.get_filters(),
                self.filter_word,
                self.filter.logic == TagFilter.Logic.AND,
                prefix=self.prefix,
                suffix=self.suffix,
                regex=self.regex,
            )
        else:
            tags = dte_instance.get_filtered_tags(
                self.get_filters(),
                self.filter_word,
                self.filter.logic == TagFilter.Logic.OR,
                prefix=self.prefix,
                suffix=self.suffix,
                regex=self.regex,
            )
        
        
        tags_in_filter = set()
        if self.filter_word:
            # Show only tags with the search words for better use
            for tag in self.filter.tags:
                if self.filter_word in tag:
                    tags_in_filter.add(tag)
        else:
            tags_in_filter = self.filter.tags
        
        tags -= tags_in_filter

        tags = dte_instance.sort_tags(
            tags=tags, sort_by=self.sort_by, sort_order=self.sort_order
        )
        tags_in_filter = dte_instance.sort_tags(
            tags=tags_in_filter, sort_by=self.sort_by, sort_order=self.sort_order
        )

        tags = tags_in_filter + tags
        
        self.visible_tags = set(tags)
        
        tags = dte_instance.write_tags(tags, self.sort_by)
        tags_in_filter = dte_instance.write_tags(tags_in_filter, self.sort_by)

        return gr.CheckboxGroup(value=tags_in_filter, choices=tags)

    def clear_filter(self):
        self.filter = TagFilter(logic=self.logic, mode=self.filter_mode)
        self.filter_word = ""
        self.selected_tags = set()
        return [self.cbg_tags_update()] + [self.filter_word]
    
    def clear_filter_output(self):
        return [self.cbg_tags, self.tb_search_tags]
