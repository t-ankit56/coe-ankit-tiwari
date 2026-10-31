from pathlib import Path

import pytest

from working_directory import working_directory


@pytest.fixture
def target(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "target"
    target.mkdir()
    return target


def test_inside_block_cwd_is_target(target):
    with working_directory(target):
        assert Path.cwd() == target


def test_after_block_cwd_is_restored(target, tmp_path):
    with working_directory(target):
        pass

    assert Path.cwd() == tmp_path
