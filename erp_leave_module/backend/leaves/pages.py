from pathlib import Path

from django.http import FileResponse

HTML_FOLDER = Path(__file__).resolve().parent / "static" / "leaves" / "html"


def _serve_page(file_name: str) -> FileResponse:
    return FileResponse(open(HTML_FOLDER / file_name, "rb"), content_type="text/html")


def login_page(request):
    return _serve_page("login.html")


def my_leaves_page(request):
    return _serve_page("my_leaves.html")


def apply_page(request):
    return _serve_page("apply.html")


def approvals_page(request):
    return _serve_page("approvals.html")
