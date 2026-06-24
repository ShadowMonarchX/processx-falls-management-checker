from pathlib import Path
import sys
import os

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def disable_local_gguf_auto_download(monkeypatch):
    monkeypatch.setenv("LOCAL_GGUF_AUTO_DOWNLOAD", "0")
