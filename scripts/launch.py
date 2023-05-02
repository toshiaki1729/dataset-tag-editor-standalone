from collections import namedtuple
import importlib.util
import os
import subprocess
import sys
import tempfile

import gradio as gr
from PIL import PngImagePlugin, Image

import cmd_args, logger
from shared_state import state


# ================================================================
# brought from AUTOMATIC1111/stable-diffusion-webui and modified

Savedfile = namedtuple("Savedfile", ["name"])
python = sys.executable


def check_python_version():
    major = sys.version_info.major
    minor = sys.version_info.minor
    micro = sys.version_info.micro

    if not (major == 3 and minor >= 9):
        logger.error(
            f"""
INCOMPATIBLE PYTHON VERSION

This program is aimed to work on Python >=3.9 (developed with 3.10.11), but you have {major}.{minor}.{micro}.
"""
        )


def cleanup_tmpdr():
    if not state.temp_dir or not state.temp_dir.is_dir():
        return

    for p in state.temp_dir.glob("**/*.png"):
        if p.is_file():
            os.remove(p)


def register_tmp_file(gradio: gr.Blocks, filename):
    if hasattr(gradio, "temp_file_sets"):  # gradio >=3.15
        gradio.temp_file_sets[0] = gradio.temp_file_sets[0] | {
            os.path.abspath(filename)
        }


def save_pil_to_file(pil_image: Image.Image):
    already_saved_as = getattr(pil_image, "already_saved_as", None)
    if already_saved_as and os.path.isfile(already_saved_as):
        from interface import interface
        register_tmp_file(interface, already_saved_as)

        file_obj = Savedfile(already_saved_as)
        return file_obj

    tmpdir = state.temp_dir
    use_metadata = False
    metadata = PngImagePlugin.PngInfo()
    for key, value in pil_image.info.items():
        if isinstance(key, str) and isinstance(value, str):
            metadata.add_text(key, value)
            use_metadata = True

    if tmpdir:
        if not tmpdir.is_dir():
            tmpdir.mkdir(parents=True)
        file_obj = tempfile.NamedTemporaryFile(delete=False, suffix=".png", dir=tmpdir)
    else:
        file_obj = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    pil_image.save(file_obj, pnginfo=(metadata if use_metadata else None))
    return file_obj


# override save to file function so that it also writes PNG info
gr.processing_utils.save_pil_to_file = save_pil_to_file


def is_installed(package):
    try:
        spec = importlib.util.find_spec(package)
    except ModuleNotFoundError:
        return False

    return spec is not None


def run(command):
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        env=os.environ,
    )


def run_pip(args, desc=None):
    if desc is not None:
        print(f"Installing {desc}")

    command = f'"{sys.executable}" -m pip {args}'
    result = run(command)
    if result.returncode != 0:
        message = f"""
Couldn't Install {desc}.
Command: {command}
Error code: {result.returncode}
stdout: {result.stdout.decode(encoding="utf8", errors="ignore") if len(result.stdout)>0 else '<empty>'}
stderr: {result.stderr.decode(encoding="utf8", errors="ignore") if len(result.stderr)>0 else '<empty>'}
"""
        raise RuntimeError(message)


# ================================================================

def prepare_environment():
    if cmd_args.opts.force_install_torch is None:
        pass
    elif cmd_args.opts.force_install_torch == "cpu":
        torch_command = "pip install -U torch torchvision"
    else:
        torch_command = f"pip install -U torch torchvision --index-url https://download.pytorch.org/whl/{cmd_args.opts.force_install_torch}"
    if (
        not is_installed("torch")
        or not is_installed("torchvision")
        or cmd_args.opts.force_install_torch is not None
    ):
        run(f'"{python}" -m {torch_command}')
    check_python_version()
    
    import devices
    logger.write(f"PyTorch device: {devices.device}")

    

if __name__ == "__main__":
    prepare_environment()

    import interface
    interface.main()
