from typing import get_type_hints
import gradio as gr

import settings, shared_state


setting_inputs = {}
restore_funcs = {}


def create_components():
    global setting_inputs
    th = get_type_hints(settings.Settings)

    for name, ty in th.items():
        s = getattr(settings.current, name)
        desc = settings.DESCRIPTIONS[name]
        if ty is int or ty is float:
            elem = gr.Number(value=s, label=desc)

            def restore(value):
                return gr.Number.update(value=value)

        elif ty is bool:
            elem = gr.Checkbox(value=s, label=desc)

            def restore(value):
                return gr.Checkbox.update(value=value)

        elif ty is str:
            elem = gr.Textbox(value=s, label=desc)

            def restore(value):
                return gr.Textbox.update(value=value)

        else:
            raise NotImplementedError()
        setting_inputs[name] = elem
        restore_funcs[name] = restore


def on_ui_tabs():
    with gr.Row():
        btn_save = gr.Button("Save Settings", variant="primary")
        btn_restore = gr.Button("Restore Default Settings")
    with gr.Column():
        create_components()
    
    btn_reload = gr.Button("Reload UI", variant="primary", elem_id="reload_ui")

    def request_restart():
        from shared_state import state
        state.interrupt()
        state.restart()

    btn_reload.click(
        fn=request_restart,
        _js="restart_reload",
        inputs=[],
        outputs=[],
    )

    def btn_save_clicked(inputs: dict):
        settings.current = settings.Settings(
            **{
                name: type(getattr(settings.current, name))(
                    inputs[setting_inputs[name]]
                )
                for name in settings.NAMES
            }
        )
        settings.save()

    btn_save.click(
        fn=btn_save_clicked,
        inputs={setting_inputs[name] for name in settings.NAMES},
    )

    def btn_restore_clicked():
        settings.restore_defaults()
        return {
            setting_inputs[name]: restore_funcs[name](getattr(settings.current, name))
            for name in settings.NAMES
        }

    btn_restore.click(fn=btn_restore_clicked, outputs=set(setting_inputs.values()))
