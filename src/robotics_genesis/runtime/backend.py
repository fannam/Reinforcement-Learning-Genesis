from __future__ import annotations


def cuda_available() -> bool:
    try:
        import torch
    except ImportError:
        return False
    return torch.cuda.is_available()


def select_backend(gs, name: str):
    """Map a backend string ('cpu'|'gpu'|'cuda') to a Genesis backend enum.

    Falls back from gpu to cpu when CUDA is unavailable, printing a notice.
    """
    normalized = name.strip().lower()
    if normalized in ("gpu", "cuda"):
        if not cuda_available():
            print("[runtime] CUDA not available, falling back to CPU backend.")
            return gs.cpu
        return gs.gpu
    if normalized == "cpu":
        return gs.cpu
    raise ValueError("backend must be 'cpu' or 'gpu'")
