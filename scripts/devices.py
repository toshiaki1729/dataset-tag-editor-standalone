import sys
import cmd_args
import torch


def has_mps():
    if sys.platform != "darwin":
        return False
    else:
        from modules import mac_specific

        return mac_specific.has_mps


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