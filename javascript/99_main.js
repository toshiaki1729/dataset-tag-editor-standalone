
let gl_dataset_images_key_handler = function (e) {
    switch (e.key) {
        case 'Enter':
            let button = gradioApp().getElementById('btn_add_image_selection');
            if (button) {
                button.click();
            }
            e.preventDefault();
            break;
    }
}

let gl_filter_images_key_handler = function (e) {
    switch (e.key) {
        case 'Delete':
            let button = gradioApp().getElementById('btn_remove_image_selection');
            if (button) {
                button.click();
            }
            e.preventDefault();
            break;
    }
}

document.addEventListener("DOMContentLoaded", function () {
    let o = new MutationObserver(function (m) {
        if (gradioApp().getElementById('ui_created') == null) return

        let elem_gl_dataset = gradioApp().getElementById("dataset_gallery")
        let elem_gl_filter = gradioApp().getElementById("filter_gallery")

        if (elem_gl_dataset) {
            elem_gl_dataset.addEventListener('keydown', gl_dataset_images_key_handler, false)
        }
        if (elem_gl_filter) {
            elem_gl_filter.addEventListener('keydown', gl_filter_images_key_handler, false)
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