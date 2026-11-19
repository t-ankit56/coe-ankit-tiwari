"""Run the five questions in questions.md at two chunk sizes and save every answer with its sources."""
import json
import time
from pathlib import Path

from rag import answer, ingest, show

HERE = Path(__file__).parent
SIZES = (300, 1000)
PAUSE_SECONDS = 3


def read_questions() -> list[str]:
    """The question column of the table in questions.md (rows that start with a number)."""
    rows = [line.split("|") for line in (HERE / "questions.md").read_text().splitlines()]
    return [cells[2].strip() for cells in rows if len(cells) > 2 and cells[1].strip().isdigit()]


if __name__ == "__main__":
    questions = read_questions()
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    for size in SIZES:
        print(f"chunk size {size}: stored {ingest(size)} chunks")
        results = []
        for question in questions:
            results.append(answer(question, size))
            # saved after every question, so a failure part-way keeps what was already answered
            (out / f"size-{size}.json").write_text(json.dumps(results, indent=2))
            (out / f"size-{size}.txt").write_text("\n\n".join(show(r) for r in results) + "\n")
            print(f"  answered {len(results)} of {len(questions)}")
            time.sleep(PAUSE_SECONDS)
