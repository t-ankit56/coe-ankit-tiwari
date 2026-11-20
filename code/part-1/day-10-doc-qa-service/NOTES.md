# Notes

- Test 6 (both prompts take `context` and `question`) passed when written: V1 and V2 already shared the human message. Kept as a guard so `answer()` can fill either prompt.
- Test 9: `source` is set to the file name (`jesc109.pdf`), not PyPDFLoader's full path, so answers show readable sources and the eval's Source check compares names that don't depend on where the folder lives.
- Test 10 (many PDFs) passed when written: the green step for test 9 already looped over every `*.pdf` instead of loading one file, which was more than that test needed. Kept as a guard.
- Test 11 (non-PDF files ignored) passed when written, as expected: the `*.pdf` glob already skips them. Kept as a guard.
- Tracing: `@traceable` on `answer()` records only the question and `k`. Recording all inputs serialised the fake model and drained its message iterator, which broke tests 14 and 16.
- Evals: ingesting NCERT chapters 9 to 11 (172 chunks) hit a 429, because the free tier counts each embedded chunk as one request (100 per minute), not each batch. Cut to pages 1–2 of chapter 10 (7 chunks) and 4 cases. With 4 cases, one case is 25 points of pass rate, so the number is coarse.
- Evals: the 2-page eval PDF is now committed instead of downloaded. The download needed a fetch script, a hash file and an extra Let's Encrypt root (ncert.nic.in chains to a root missing from trust stores), which was setup, not part of the service.
- Evals: 5-second pause before every chat call (generation and judge), because Day 9 hit 429 at 2 seconds against the free-tier 15 requests per minute.
- Live run: Gemini 3 replies with a list of content blocks, so `reply.content` reached DeepEval as a list and the first v1 run crashed before judging (4 embeddings + 4 generations lost). Test 18 covers it; `answer()` now returns `reply.text`. The suite also saves answers before judging.
- Results: v1 0/4, v2 4/4. v1 got all three facts right (judge 1.0) but never cited `[n]`, and on none-01 it answered "concave lens" from outside knowledge (judge 0.2), although the 2 pages don't say it. v2 cited every answer and said "I don't know". none-01 under v1 is the failure kept for the presentation.
- `PASS_RATE` = 0.75, one case below the v2 result of 1.0: with 4 cases, 1.0 would fail CI on a single wobble. A drop to v1 behaviour (0/4) still fails clearly.
- Evals: each case is a test, but a failing case is `xfail` with its reason, so the pass rate is the only gate. Otherwise one failing case would fail every CI run and `PASS_RATE` would mean nothing.
