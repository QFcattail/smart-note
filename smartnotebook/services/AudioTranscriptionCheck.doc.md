# AudioTranscriptionCheck.py — 录音文件转写：查任务取文稿

`main(task_id)`：查询 `aip.baidubce.com/rpc/2.0/aasr/v1/query`，任务仍在 `Running` 时返回 `0`，完成后返回带时间戳的文稿（`format_milliseconds` 把毫秒转「X分Y秒」前缀，每句一行）。界面在课程页点「提问」时经 `function.is_task_running` 调用一次，不做定时轮询。

- 与 Create 共用 `BAIDU_TRANSCRIBE_API_KEY` / `BAIDU_TRANSCRIBE_SECRET_KEY`

## 坑点

- 百度侧转写有分钟级延迟，未完成时界面只提示「正在转写」，需要用户稍后再点
- 任务失败（音频下载失败 / 格式不支持）时返回「转写失败：<百度错误信息>」，它会像正常文稿一样存进 `doc`；要重试需删掉课程重新建

---

## English

`main(task_id)` queries the transcription endpoint once: returns `0` while the task is `Running`, otherwise the timestamped transcript ("X分Y秒" prefixes via `format_milliseconds`, one sentence per line). The UI calls it via `function.is_task_running` only when the user taps "ask" on a course page — there is no periodic polling. Shares the `BAIDU_TRANSCRIBE_*` credentials with Create. Pitfalls: transcription takes minutes, so the user has to retry later; failed tasks return "转写失败：<Baidu error message>", which gets stored in `doc` like a transcript — delete and recreate the course to retry.
