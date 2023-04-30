let ModifiedGallery_dataset = new ModifiedGallery()
let ModifiedGallery_filter = new ModifiedGallery()


function gl_dataset_images_selected_index() {
    return ModifiedGallery_dataset.getSelectedIndex()
}

function gl_filter_images_selected_index() {
    return ModifiedGallery_filter.getSelectedIndex()
}

function gl_dataset_images_filter(indices) {
    ModifiedGallery_dataset.filter(indices)
    return indices
}

function gl_dataset_images_clear_filter() {
    ModifiedGallery_dataset.clearFilter()
    return []
}

function gl_dataset_images_close() {
    ModifiedGallery_dataset.clickClose()
}

function gl_filter_images_close() {
    ModifiedGallery_filter.clickClose()
}

let gl_dataset_images_clicked = function () {
    ModifiedGallery_dataset.updateFilter()
    ModifiedGallery_dataset.clickHandler()
    let set_button = gradioApp().getElementById("btn_hidden_set_index");
    if (set_button) {
        set_button.click()
    }
}

let gl_dataset_images_next_clicked = function () {
    ModifiedGallery_dataset.updateFilter()
    ModifiedGallery_dataset.clickNextHandler()
    let set_button = gradioApp().getElementById("btn_hidden_set_index");
    if (set_button) {
        set_button.click()
    }
}

let gl_dataset_images_close_clicked = function () {
    ModifiedGallery_dataset.updateFilter()
    ModifiedGallery_dataset.clickCloseHandler()
    let set_button = gradioApp().getElementById("btn_hidden_set_index");
    if (set_button) {
        set_button.click()
    }
}

let gl_dataset_images_key_handler = function (e) {
    ModifiedGallery_dataset.keyHandler(e)
    switch (e.key) {
        case 'Enter':
            let button = gradioApp().getElementById('btn_add_image_selection');
            if (button) {
                button.click();
            }
            e.preventDefault();
            break;
    }
    let set_button = gradioApp().getElementById("btn_hidden_set_index");
    if (set_button) {
        set_button.click()
    }
}


let gl_filter_images_clicked = function () {
    ModifiedGallery_filter.updateFilter()
    ModifiedGallery_filter.clickHandler()
    let set_button = gradioApp().getElementById("btn_hidden_set_selection_index");
    if (set_button) {
        set_button.click()
    }
}

let gl_filter_images_next_clicked = function () {
    ModifiedGallery_filter.updateFilter()
    ModifiedGallery_filter.clickNextHandler()
    let set_button = gradioApp().getElementById("btn_hidden_set_selection_index");
    if (set_button) {
        set_button.click()
    }
}

let gl_filter_images_close_clicked = function () {
    ModifiedGallery_filter.updateFilter()
    ModifiedGallery_filter.clickCloseHandler()
    let set_button = gradioApp().getElementById("btn_hidden_set_selection_index");
    if (set_button) {
        set_button.click()
    }
}

let gl_filter_images_key_handler = function (e) {
    ModifiedGallery_filter.keyHandler(e)
    switch (e.key) {
        case 'Delete':
            let button = gradioApp().getElementById('btn_remove_image_selection');
            if (button) {
                button.click();
            }
            e.preventDefault();
            break;
    }
    let set_button = gradioApp().getElementById("btn_hidden_set_selection_index");
    if (set_button) {
        set_button.click()
    }
}

document.addEventListener("DOMContentLoaded", function () {
    let o = new MutationObserver(function (m) {
        if (gradioApp().getElementById('ui_created') == null) return

        let elem_gl_dataset = gradioApp().getElementById("dataset_gallery")
        let elem_gl_filter = gradioApp().getElementById("filter_gallery")

        if (elem_gl_dataset) {
            ModifiedGallery_dataset.setElement(elem_gl_dataset)
            ModifiedGallery_dataset.addKeyHandler(gl_dataset_images_key_handler)
            ModifiedGallery_dataset.addClickHandler(gl_dataset_images_clicked)
            ModifiedGallery_dataset.addClickNextHandler(gl_dataset_images_next_clicked)
            ModifiedGallery_dataset.addClickCloseHandler(gl_dataset_images_close_clicked)
        }
        if (elem_gl_filter) {
            ModifiedGallery_filter.setElement(elem_gl_filter)
            ModifiedGallery_filter.addKeyHandler(gl_filter_images_key_handler)
            ModifiedGallery_filter.addClickHandler(gl_filter_images_clicked)
            ModifiedGallery_filter.addClickNextHandler(gl_filter_images_next_clicked)
            ModifiedGallery_filter.addClickCloseHandler(gl_filter_images_close_clicked)
        }

        function changeTokenCounterPos(id, id_counter) {
            var prompt = gradioApp().getElementById(id)
            var counter = gradioApp().getElementById(id_counter)

            if (counter.parentElement == prompt.parentElement) {
                return
            }

            prompt.parentElement.insertBefore(counter, prompt)
            prompt.parentElement.style.position = "relative"
            counter.style.width = "auto"
        }
        changeTokenCounterPos('dte_caption', 'dte_caption_counter')
        changeTokenCounterPos('dte_edit_caption', 'dte_edit_caption_counter')
        changeTokenCounterPos('dte_interrogate', 'dte_interrogate_counter')
    });

    o.observe(gradioApp(), { childList: true, subtree: true })
});