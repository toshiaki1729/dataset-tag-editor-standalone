function ask_save_change_or_not(idx) {
    if (idx < 0) {
        return -1
    }
    res = window.confirm(`Save changes in captions?`)
    if (res) {
        let set_button = gradioApp().getElementById("btn_hidden_save_caption");
        if (set_button) {
            set_button.click()
        }
    }
}