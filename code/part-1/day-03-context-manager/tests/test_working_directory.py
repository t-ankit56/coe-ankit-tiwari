from pathlib import Path

from working_directory import working_directory


def test_inside_block_cwd_is_target(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "target"
    target.mkdir()

    with working_directory(target):
        assert Path.cwd() == target
