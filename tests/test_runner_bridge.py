#!/usr/bin/env python3
import pytest
from pathlib import Path
from runner_bridge import make_subprocess_runner

def test_subprocess_runner_unknown_backend():
    runner = make_subprocess_runner({})
    res = runner("nonexistent", "hello")
    assert res.exit_code == 2
    assert "unknown_backend" in res.stderr
