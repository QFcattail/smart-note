# SpeechRecognize.py — 百度语音识别封装

`main(FilePath)`：读 wav 文件 → base64 → POST `vop.baidu.com/server_api`，返回识别文本。

- 凭据读环境变量 `BAIDU_ASR_API_KEY` / `BAIDU_ASR_SECRET_KEY`
- 调用方：`function.create_keyword_speech` / `change_title_speech` / `course_question_speech` 及问答录音

## 坑点

- 只认 wav（采样率等参数百度端有要求）；现场录音保存为 `wave.wav`，格式不对会报错或识别为空
- 长语音走这个接口会截断，长音频应走录音文件转写（`AudioTranscription*.py`）

---

## English

Wrapper for Baidu speech recognition: `main(FilePath)` sends a wav file (base64) to the ASR API and returns text. Credentials from `BAIDU_ASR_API_KEY` / `BAIDU_ASR_SECRET_KEY`. Pitfalls: wav-only (the live recording lands in `wave.wav`; wrong formats error out or return empty); long audio gets truncated — use the transcription endpoints (`AudioTranscription*.py`) instead.
