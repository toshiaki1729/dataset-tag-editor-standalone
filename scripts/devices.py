import sys
import cmd_args
import torch


# ================================================================
# borrowed from AUTOMATIC1111/stable-diffusion-webui

# has_mps is only available in nightly pytorch (for now) and macOS 12.3+.
# check `getattr` and try it for compatibility
def check_for_mps() -> bool:
    if hasattr(torch, "backends"):
        return torch.backends.mps.is_available()
    elif not getattr(torch, "has_mps", False):
        return False
    
    try:
        torch.zeros(1).to(torch.device("mps"))
        return True
    except Exception:
        return False


_has_mps = check_for_mps()

# ================================================================


def has_mps():
    if sys.platform != "darwin":
        return False
    else:
        return _has_mps


def get_cuda():
    if cmd_args.opts.device_id is not None:
        return torch.cuda.device(f"cuda:{cmd_args.opts.device_id}")
    else:
        return torch.cuda.device("cuda")


def get_cuda_device():
    if cmd_args.opts.device_id is not None:
        return torch.device(f"cuda:{cmd_args.opts.device_id}")
    else:
        return torch.device("cuda")


def get_optimal_device():
    if torch.cuda.is_available():
        return get_cuda_device()

    if has_mps():
        torch.device("mps")

    try:
        import torch_directml
        return torch_directml.device()
    except:
        pass

    return torch.device("cpu")


# from AUTOMATIC1111's SDwebUI
def torch_gc():
    if torch.cuda.is_available():
        with get_cuda():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()


device = get_optimal_device()
cpu = torch.device("cpu")
