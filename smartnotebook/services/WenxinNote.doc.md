# WenxinNote.py — 文心千帆对话封装（笔记条目生成）

骨架与 `WenxinSingle.py` 完全一致（token → 流式请求 → pyee 增量事件），签名 `(prompt, note, keyword)`：调用方 `function.create_keyword_ocr/speech` 拼好「关键词 → 讲解式笔记」的 prompt，生成结果与配图一起落成一条关键词条目。凭据 `BAIDU_WENXIN_*`。

## 坑点

见 `WenxinSingle.doc.md`（共用骨架共坑）。

---

## English

Same skeleton as `WenxinSingle.py` with signature `(prompt, note, keyword)`: `function.create_keyword_ocr/speech` builds the "keyword → explanatory note" prompt; the streamed result becomes one keyword entry together with the photo. Credentials via `BAIDU_WENXIN_*`. See `WenxinSingle.doc.md` for shared pitfalls.
