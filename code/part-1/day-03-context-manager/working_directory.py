import os
from pathlib import Path
from types import TracebackType


class working_directory:
    def __init__(self, path: str | os.PathLike[str]) -> None:
        self._path = path

    def __enter__(self) -> Path:
        self._previous = Path.cwd()
        os.chdir(self._path)
        return Path.cwd()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        os.chdir(self._previous)
