from __future__ import annotations

from dataclasses import dataclass
from os import cpu_count


@dataclass(frozen=True)
class DeviceInfo:
    # Hardware profile used to drive model loading and runtime decisions.
    device: str
    gpu_name: str | None = None
    vram_gb: float | None = None
    ram_gb: float | None = None
    cpu_cores: int | None = None
    os_name: str | None = None


def get_device_info() -> DeviceInfo:
    import platform

    device = "cpu"
    gpu_name = None
    vram_gb = None
    ram_gb = None

    try:
        import torch  # type: ignore

        # Prefer CUDA when available because it provides the best
        # inference performance and supports full model offloading.
        if torch.cuda.is_available():
            device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            props = torch.cuda.get_device_properties(0)
            vram_gb = round(props.total_memory / (1024**3), 2)

        # Apple Silicon MPS is the preferred fallback accelerator.
        elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            device = "mps"

    except Exception:
        # Hardware detection must never block application startup.
        device = "cpu"

    try:
        import psutil  # type: ignore

        # Memory information helps validate model compatibility.
        ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    except Exception:
        ram_gb = None

    return DeviceInfo(
        device=device,
        gpu_name=gpu_name,
        vram_gb=vram_gb,
        ram_gb=ram_gb,
        cpu_cores=cpu_count(),
        os_name=platform.system().lower(),
    )


def detect_device() -> DeviceInfo:
    # Centralized entry point for hardware detection.
    return get_device_info()
