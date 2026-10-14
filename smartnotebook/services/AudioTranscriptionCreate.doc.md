# AudioTranscriptionCreate.py — 录音文件转写：建任务

`main(vedio_url)`：向 `aip.baidubce.com/rpc/2.0/aasr/v1/create` 提交音频 URL，返回百度转写 `task_id`（由 `function.set_url` 存入 `case.yaml` 的 `course_case.<num>.task_id`）。

- 凭据读环境变量 `BAIDU_TRANSCRIBE_API_KEY` / `BAIDU_TRANSCRIBE_SECRET_KEY`
- 音频必须是公网可直达的 URL（mp4/mp3/wav 等，按百度文档限制）

## 坑点

- 本地文件不能直接转写：先传到可公开访问的存储再给 URL
- task_id 只是受理凭证，文稿要等 `AudioTranscriptionCheck` 轮询

---

## English

Submits an audio URL to Baidu's file-transcription create endpoint and returns a `task_id` (stored by `function.set_url` into `case.yaml`). Credentials from `BAIDU_TRANSCRIBE_API_KEY` / `BAIDU_TRANSCRIBE_SECRET_KEY`. The audio must be a publicly reachable URL — local files need uploading first; the transcript itself is fetched by polling `AudioTranscriptionCheck`.
