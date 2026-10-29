# Makes `python3 -m pytest` work from the repo root without installing.
import pathlib
import sys

SRC = pathlib.Path(__file__).parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


import socket

import pytest


@pytest.fixture(autouse=True)
def _no_real_network(monkeypatch):
    """Fail loudly if any test tries to open a real connection."""

    def refuse(*args, **kwargs):
        raise AssertionError("real network access attempted in tests")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)
