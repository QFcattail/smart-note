# 架构与数据

PyQt5 桌面应用，全部 AI 能力来自百度智能云 REST API，无本地模型。数据落在一个 YAML 文件加一个图片目录里。

## 分层规则与模块分工

代码按前后端分层收在 `smartnotebook/` 包内，依赖方向固定为 **ui → core → services**：

| 层 | 目录 | 职责 | 禁止事项 |
| --- | --- | --- | --- |
| 前端界面层 | `ui/` | 交互、拍照 / 录音采集、线程调度、信号渲染 | 不直接 `open` 数据文件，不拼 prompt |
| 业务核心层 | `core/` | `function.py`：`case.yaml` 唯一读写者、业务校验（字数限制、未识别兜底）、prompt 组装、流程编排 | 不写界面代码 |
| 外部服务层 | `services/` | 百度 OCR / 语音识别 / 录音转写 / 文心千帆、SMTP 邮件、WiFi 检测的无状态封装 | 不落盘、不 import ui/core，凭据只从环境变量读 |

约定俗成的放宽：界面层允许**直接订阅** `services/` 里 Wenxin 封装的事件（流式上屏），但任何写数据动作必须经 `core/function.py`。

模块明细（路径相对 `smartnotebook/`）：

| 文件 | 职责 |
| --- | --- |
| `main.py` / `app.py` | 入口与主菜单调度（研学笔记 / 实时问答 / 录课整理 / 设置四页切换、时钟、WiFi 状态） |
| `ui/mainui.py` | 主菜单布局；`ui/*ui.py` / `ui/*uic.py` 为各功能页 |
| `ui/noteui*.py` | 研学笔记：笔记列表、新建、关键词管理、正文配图浏览、导出 |
| `ui/qaui*.py` / `ui/qahistoryui*.py` / `ui/qaresultui*.py` | 实时问答、问答历史与结果页 |
| `ui/courseui*.py` / `ui/createcourseui*.py` / `ui/courseinputui*.py` | 录课整理：课程列表、新建课程（扫码录入 URL）、视频播放、转写状态查询与提问 |
| `ui/inputui*.py` / `ui/settinginputui*.py` | 笔记标题 / 关键词 / 配图输入页（拍照或录音），设置项扫码录入页 |
| `core/function.py` | 业务中枢：`case.yaml` 读写、笔记 / 课程 / 关键词 / 问答的增删查，串联「输入→识别→生成→存储」 |
| `services/OCR.py` | 百度手写文字识别（图片 base64 → 文字） |
| `services/SpeechRecognize.py` | 百度语音识别（wav → 文字） |
| `services/AudioTranscriptionCreate.py` / `services/AudioTranscriptionCheck.py` | 百度录音文件转写：建任务 / 查任务取文稿 |
| `services/WenxinSingle.py` / `services/WenxinNote.py` / `services/WenxinCourse.py` / `services/WenxinQa.py` / `services/WenxinFlow.py` | 文心千帆 ERNIE 对话封装（问答 / 笔记扩写 / 录课时间定位；Single、Flow 当前未被界面调用），流式返回 |
| `services/mailUtils.py` | SMTP 邮件导出：笔记 HTML 内嵌配图后整封发送 |
| `services/wifiUtils.py` | 联网检测（能否访问 baidu.com）与按设置页 SSID/密码用 pywifi 连接 |
| `data/case.yaml`（仓库根 `data/`） | **全部业务数据**（见下） |
| `script/install.ps1` / `script/launch.ps1`（仓库根 `script/`） | 建 venv 装依赖 / 锚定仓库根后启动 `python smartnotebook\main.py` |

命名规律：`xxxui.py` 是 Qt Designer 导出的界面布局，`xxxuic.py` 是对应的事件逻辑。手写模块旁均配 `<文件名>.doc.md`（中英双语）；界面布局文件按本节集体说明，不逐个配文档。

## 数据流动

三条功能线共用「输入 → 大模型理解 → 输出」主干，具体到模块：

**A. 拍照笔记**

1. `ui/inputuic.py` 调摄像头拍照，界面先显示加载占位图
2. `core/function.create_keyword_ocr` 把画面 `cv2 → base64` 交给 `services/OCR.py` → 手写识别得到关键词文本
3. `core` 先写入一条 `{keyword, content: "", img: 占位图}`，再调 `services/WenxinNote.main` 流式生成讲解 HTML
4. 每段增量经 `new_introduction` 事件到 `ui/createnoteuic.py`，由 `core.add_content` 追加进 `content` 并刷新界面
5. 配图单独拍：点配图区域 → `ui/inputuic.py` 存 `data/img/<时间戳>.png` → `core.change_img` 替换占位图路径

**B. 语音问答**

1. `ui/qauic.py` 录音（仓库根 `wave.wav`）或拍照 → `core/function.get_question_speech` / `get_question_ocr` 调 `services/SpeechRecognize.py` / `services/OCR.py` 得到问题文本
2. `core` 先做本地校验（超过 50 字 / 未识别直接发占位回答），通过后拼上「备注资料来源、明显的考试题可拒答」的提示词 → `services/WenxinQa` 流式生成
3. 回答渲染为 `QandA_html`，`core.record_qa_history` 写入 `qa_history_list`

**C. 录课整理**

1. `ui/createcourseuic.py` 新建课程后进入 `ui/courseinputuic.py`，扫描内容为 mp4 URL 的二维码
2. `core/function.set_url` 写入 URL，并调 `services/AudioTranscriptionCreate.py` 提交转写任务，`task_id` 存入 `course_case`；界面同时用 `QMediaPlayer` 播放该视频
3. 用户点「提问」时 `core.is_task_running` 调 `services/AudioTranscriptionCheck.py` 查一次任务：未完成则按钮显示「正在转写」；完成则把带「X分Y秒」前缀的文稿存入 `course_case.doc`
4. 提问（拍照 / 录音）后，`core.course_question_*` 把问题和整份文稿拼进 prompt，`services/WenxinCourse` 流式返回相关内容所在的时间点（不落盘）

**D. 邮件导出**

1. `ui/noteuic.py` 点「导出笔记」进入导出模式，再点列表中的笔记 → `core.export_note` 读出整篇笔记的关键词条目组装 HTML（每 4 个关键词一封）
2. `services/mailUtils.py` 把配图转 MIME 内嵌，长笔记自动拆成多封，SMTP 发到设置页保存的收件邮箱

## 模块通讯

| 机制 | 用在哪 | 说明 |
| --- | --- | --- |
| **Qt 信号槽**（`pyqtSignal`） | 每个 `*uic.py` 窗口类定义 `conn = pyqtSignal(object)`（问答页另有 `vedioconn` / `voiceconn`） | 工作线程 `emit` 结果，主线程槽函数更新界面——跨线程刷新的标准做法 |
| **业务信号**（`core` 自定义） | `function.py` 的 `ee_question` / `ee_course_question` / `ee_return_create` / `ee_return_create_course` | core 校验或落库后主动通知界面（如「返回新建页」），界面预先 `.connect` 订阅 |
| **pyee 事件流** | `services/Wenxin*.py` 的 `AsyncIOEventEmitter` | aiohttp 流式响应逐行 `ee.emit('new_result' / 'new_introduction', …)`，界面订阅实现逐字上屏；core 出错时代发占位事件（如 `WenxinQa.ee.emit('new_result', "未识别")`） |
| **后台线程** | `main.py`（每 2 秒检测能否访问 baidu.com）、各 `*uic.py` 的录音线程 | 把阻塞的网络检测 / 录音挪出 UI 事件循环，结果经信号回主线程 |
| **QTimer** | 主窗时钟（1 秒）、各输入页摄像头取景刷新（约 30 帧/秒） | 转写任务不定时轮询，只在点「提问」时查一次 |
| **YAML 数据总线** | `data/case.yaml` | 全库唯一持久化文件，**只有 `core/function.py` 读写**（56 处集中一处）；ui/services 均不直接触达 |

## 数据存储：`data/case.yaml`

六个顶层键，增删都由 `core/function.py` 完成：

```yaml
course_case:          # 录课转写与整理结果，键为课程编号
  1:
    doc: '19分24秒 下面我和同学们谈谈……'   # 转写文稿，每行「X分Y秒 内容」
    task_id: '656aba89c292520001747832'    # 百度转写任务号
    url: https://example.com/lesson.mp4    # 课程视频直链
course_list:          # 课程索引
- date: '2024-03-22'
  name: new_course
  num: 5
email_account: 'you@example.com'   # 设置页保存的收件邮箱
keywords:            # 每篇笔记的关键词内容，键为笔记编号
  1:
  - keyword: 古文化街          # 关键词（列表页标题）
    content: '<p>正文 HTML……'   # 大模型生成的讲解
    img: data/img/1711188018.png    # 配图路径（相对仓库根）
note_list:           # 笔记索引（date/name/num 同 course_list）
- date: '2024-03-23'
  name: 天津市旅游
  num: 1
qa_history_list:     # 问答历史
- question: 灯火阑珊这个词的用法
  QandA_html: '<h1>……</h1><p>……</p>'   # 问 + 答渲染后的 HTML
  date: '2023-12-02'
  num: 0
```

WiFi 名称与密码不落盘：设置页输入框或扫码录入的值只存 `function.py` 的内存全局变量（`restore_ssid` / `restore_password`），点保存时立即尝试用 pywifi 连接，重启应用后需重填；设置页里持久化的只有收件邮箱。仓库自带的 `data/case.yaml` 是只含六个空键的骨架，代码不会自动补键——想清空数据时恢复成这个骨架即可，不要删成空文件。配图在 `data/img/`（不入库，启动时自动创建）。**整个 `data/` 目录备份即全量备份。**

## 二开提示

- 加一种「输入方式」：在 `core/function.py` 写一个 `create_keyword_xxx(note)`，界面侧挂按钮即可，存储格式不用动
- 换大模型：`services/` 里 5 个 `Wenxin*.py` 共用同一套 token 获取与请求骨架，照抄一个改 payload 就行
- 换邮箱服务商：改 `services/mailUtils.py` 的 `smtplib.SMTP_SSL(...)` 一行
- `case.yaml` 里的 HTML 都是富文本，`noteui` 用 `QTextBrowser` 渲染，注意别引入外链资源
- 写 `case.yaml` 是全量覆写且无锁：若引入后台线程直接写数据，先加锁或收敛到 core 的单线程队列

---

## English

A PyQt5 desktop app; every AI capability is a Baidu Cloud REST call, no local models.

**Layering** — code is layered inside the `smartnotebook/` package with a fixed dependency direction `ui → core → services`: `ui/` handles interaction, capture, threading and signal rendering (never opens data files, never builds prompts); `core/function.py` is the single owner of `data/case.yaml`, does validation and prompt assembly; `services/` are stateless transport wrappers (Baidu OCR / ASR / transcription / ERNIE, SMTP, Wi-Fi) that read credentials from environment variables only. One deliberate relaxation: the UI may subscribe directly to streaming events emitted by the ERNIE wrappers, but every write goes through `core`.

**Data flows** — (A) photo note: camera frame → `OCR` → keyword entry with a placeholder image → `WenxinNote` streams HTML appended via `core.add_content`; the keyword's photo is taken separately by tapping the image area (saved to `data/img/`, set via `core.change_img`); (B) QA: photo or `wave.wav` recording → `OCR` / `SpeechRecognize` → local validation (50-char limit) → `WenxinQa` streaming → `qa_history_list`; (C) lecture: scan a QR code holding the mp4 URL → `AudioTranscriptionCreate` job (video plays in `QMediaPlayer`) → on tapping "ask", `AudioTranscriptionCheck` is queried once and the timestamped transcript stored in `course_case.doc` → `WenxinCourse` locates the timestamps relevant to the question (not persisted); (D) export: enter export mode, tap a note → HTML with embedded images over SMTP, four keywords per mail.

**Module communication** — Qt signal/slot (`conn = pyqtSignal(object)` per window) for cross-thread UI updates; custom core signals (`ee_question`, `ee_return_create`, …) for business callbacks; `pyee.AsyncIOEventEmitter` in the ERNIE wrappers for token-by-token streaming; background threads for recording and the 2-second baidu.com connectivity check; `QTimer` for the clock and camera preview (transcription status is checked on demand, not polled). `data/case.yaml` is the single persistent file, written only by `core/function.py` (full-file rewrite, no lock). Schema of its six top-level keys is documented above; the whole `data/` folder is the full backup unit.

**Extending** — add an input method as `create_keyword_xxx` in `core/function.py`; swap the LLM by copying one of the five `Wenxin*.py` wrappers; change the mail provider in one line of `services/mailUtils.py`.
