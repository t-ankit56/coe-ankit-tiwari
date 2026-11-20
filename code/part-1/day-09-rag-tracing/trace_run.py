"""Run the five questions from questions.md once at chunk size 600 and save latency, tokens and cost per step."""
import json
import re
import time
from pathlib import Path

from langsmith.run_trees import get_cached_client

import rag

SIZE = 600
PAUSE_SECONDS = 2
ROOT = Path(__file__).parent


def questions() -> list[str]:
    """The second column of the table rows in questions.md."""
    rows = re.findall(r"^\| \d+ \| (.+?) \|", (ROOT / "questions.md").read_text(), re.M)
    return rows


if __name__ == "__main__":
    runs = []
    for i, question in enumerate(questions()):
        if i:
            time.sleep(PAUSE_SECONDS)
        rag.STEPS.clear()
        start = time.perf_counter()
        result = rag.answer(question, SIZE)
        runs.append({"question": question, "answer": result["answer"], "total_seconds": round(time.perf_counter() - start, 3),
                     "steps": list(rag.STEPS)})
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "run.json").write_text(json.dumps(runs, indent=2) + "\n")
    get_cached_client().flush()  # make sure every trace is uploaded before the process exits
    print(f"saved results/run.json for {len(runs)} questions")
