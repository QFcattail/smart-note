# WenxinQa.py — 文心千帆对话封装（实时问答）

骨架同 `WenxinSingle.py`，签名 `(prompt)`：实时问答页把语音识别出的问题直接发给模型，回答渲染成 `QandA_html` 存入 `qa_history_list`。凭据 `BAIDU_WENXIN_*`。共用坑点见 `WenxinSingle.doc.md`。

---

## English

Same skeleton as `WenxinSingle.py`, signature `(prompt)`: the QA page sends the speech-recognized question straight to the model; answers are rendered into `QandA_html` and appended to `qa_history_list`. Credentials `BAIDU_WENXIN_*`; shared pitfalls in `WenxinSingle.doc.md`.
