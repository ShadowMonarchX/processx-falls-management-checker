from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceInfo:
    device: str
    gpu_name: str | None = None
    vram_gb: float | None = None
    ram_gb: float | None = None
    cpu_cores: int | None = None
    os_name: str | None = None


def detect_device() -> DeviceInfo:
    import platform

    device = "cpu"
    gpu_name = None

    try:
        import torch  # type: ignore

        if torch.cuda.is_available():
            device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
        elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            device = "mps"
    except Exception:
        device = "cpu"

    return DeviceInfo(
        device=device,
        gpu_name=gpu_name,
        cpu_cores=__import__("os").cpu_count(),
        os_name=platform.system().lower(),
    )
