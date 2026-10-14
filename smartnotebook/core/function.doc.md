# function.py — 业务中枢

全部业务数据的读写与「输入 → 识别 → 生成 → 存储」流程的串联都在这里；改数据结构先改本文件。

## 关键函数（按用途分组）

- **数据访问**：`read_yaml`（唯一 YAML 入口，UTF-8）、`get_note_list` / `get_course_list` / `get_title` / `get_date` / `get_keywords` / `get_content` / `get_img_path`（列表页与详情页取数）
- **增删**：`create_note` / `create_course` / `delete_note` / `delete_course` / `add_content` / `delete_keyword` / `change_img` / `set_url`
- **智能入口（被界面按钮调用）**：`create_keyword_ocr` / `create_keyword_speech`（关键词→OCR/语音→Wenxin 生成笔记条目）、`course_question_ocr` / `course_question_speech`（对课程内容提问）、`change_title_speech` / `change_title_ocr`（标题语音/拍照输入）、`record_qa_history` / `get_qa_history_*`（问答历史）
- **转写状态**：`is_task_running`（课程页点「提问」时查一次百度转写任务，完成则把文稿存入 `doc`）
- **设置**：`get_email_account` / `change_email_account`（落盘）；`restore_ssid` / `restore_password` / `get_ssid` / `get_password`（**仅内存全局变量**）

## 坑点

- 所有写操作都是「read_yaml → 改 dict → 全量写回」，并发调用会互相覆盖（当前单线程界面下无碍，二次开发加线程时注意加锁）
- 五个 `Wenxin*.py` 的语义差异（笔记整理/课程整理/问答）由本文件拼的 prompt 决定，Wenxin 文件本身只是传输层
- `find_index_by_*` 在找不到时抛 IndexError——数据被手工改坏时的典型崩溃点

---

## English

The business hub: every read/write of business data and the "input → recognize → generate → store" pipelines. Groups: data access (`read_yaml`, `get_*` family), CRUD (`create_*`/`delete_*`/`add_content`/`change_img`/`set_url`), smart entry points called by UI buttons (`create_keyword_ocr/speech`, `course_question_*`, `change_title_*`, `record_qa_history`), transcription polling (`is_task_running`), and settings (mailbox persisted; SSID/password in-memory only). Pitfalls: writes are read-modify-write of the whole file (no locking — fine in the single-threaded UI, add locks before threading); the semantic differences between the five `Wenxin*.py` wrappers come from prompts built here; `find_index_by_*` raises IndexError on corrupted data.
