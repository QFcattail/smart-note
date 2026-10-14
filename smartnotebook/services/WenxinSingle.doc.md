# WenxinSingle.py — 文心千帆单轮对话封装（传输层）

五个 `Wenxin*.py`（Single/Note/Course/Qa/Flow）共用同一骨架，本文件是基准实现：

- `get_access_token()`：`BAIDU_WENXIN_API_KEY` / `BAIDU_WENXIN_SECRET_KEY` 换 token
- `mainreque(prompt, note, keyword)`：aiohttp 流式请求 ERNIE chat/completions，增量结果经 `pyee` 事件发射（界面逐字上屏）
- `main(...)`：同步包装（事件循环里跑一次 mainreque）

**语义差异不在这些文件里**：`function.py` 负责按用途拼 prompt 再选一个封装调用。Single/Note 签名带 `(prompt, note, keyword)`（笔记上下文），Course/Qa/Flow 只带 `(prompt)`。

## 坑点

- token 每次现取；流中断时已发事件不回滚，界面要做超时兜底
- 想换模型：改各文件 URL 里的 endpoint（`wenxinworkshop/chat/completions` 为 ERNIE Bot 默认）

---

## English

Base implementation of the five shared-skeleton ERNIE wrappers: `get_access_token()` (env credentials) → `mainreque()` (aiohttp streaming chat completion, incremental results emitted via pyee events) → sync `main()`. The semantic differences (note summarizing / course organizing / QA) live in the prompts assembled by `function.py`, not here; Single/Note carry `(prompt, note, keyword)`, Course/Qa/Flow just `(prompt)`. Pitfalls: tokens are fetched per call; interrupted streams leave already-emitted events — the UI needs a timeout fallback; to swap models change the endpoint in the URL.
