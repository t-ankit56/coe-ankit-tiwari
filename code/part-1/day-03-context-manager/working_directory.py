import os


class working_directory:
    def __init__(self, path: str | os.PathLike[str]) -> None:
        self._path = path

    def __enter__(self) -> None:
        os.chdir(self._path)

    def __exit__(self, exc_type, exc, tb) -> None:
        pass
