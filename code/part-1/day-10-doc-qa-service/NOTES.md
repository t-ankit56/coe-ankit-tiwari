# Notes

- Test 6 (both prompts take `context` and `question`) passed when written: V1 and V2 already shared the human message. Kept as a guard so `answer()` can fill either prompt.
- Test 9: `source` is set to the file name (`jesc109.pdf`), not PyPDFLoader's full path, so answers show readable sources and the eval's Source check compares names that don't depend on where the folder lives.
