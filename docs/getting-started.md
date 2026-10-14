# 新手入门

从零把「智能研学笔记本」跑起来：装环境、配百度智能云密钥、走通拍照记笔记 → 语音问答 → 邮件导出全流程。

## 它是什么

一台随身答疑学习机（树莓派 + 4 英寸触摸屏）的软件，也能在 Windows 电脑上运行：**拍下展板 / 讲义，自动识别文字并请大模型写成讲解式笔记，再配上你拍的照片；拍照或录音提问，大模型作答；扫一个课程录像链接的二维码，转写后能按问题定位到视频里的时间点**，最后把笔记用邮件发给自己。

## 环境要求

- Windows 10 / 11，Python 3.9
- 摄像头（必需：拍照输入、扫码录入都靠它，笔记本自带的即可）、麦克风（语音输入，可选）
- 网络（所有 AI 能力都是云端 API）

## 安装

1. 把仓库放到一个**纯英文路径**下（如 `D:\smart-notebook`）
2. 右键 `script/install.ps1` →「使用 PowerShell 运行」：自动创建 venv 并按 `requirements.txt` 安装全部依赖（默认走清华镜像，海外网络可删掉脚本里的 `-i` 参数）
3. 右键 `script/launch.ps1` →「使用 PowerShell 运行」：启动主界面「智能研学笔记」

若提示「禁止运行脚本」，先用管理员 PowerShell 执行 `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`。

## 配置密钥（关键一步）

代码不含任何密钥，全部从**环境变量**读取。先到[百度智能云控制台](https://console.bce.baidu.com/) → 千帆/人工智能服务，分别创建 4 个应用（每个应用会得到一对 API Key / Secret Key），再设置环境变量：

| 用途 | 控制台入口（应用类型） | 环境变量 |
| --- | --- | --- |
| 手写文字识别（拍照 → 文字） | 文字识别 · 手写文字识别 | `BAIDU_OCR_API_KEY` / `BAIDU_OCR_SECRET_KEY` |
| 语音识别（说话 → 文字） | 语音技术 · 语音识别 | `BAIDU_ASR_API_KEY` / `BAIDU_ASR_SECRET_KEY` |
| 录音文件转写（课程录像 → 文稿） | 语音技术 · 录音文件转写 | `BAIDU_TRANSCRIBE_API_KEY` / `BAIDU_TRANSCRIBE_SECRET_KEY` |
| 大模型（笔记整理 / 问答） | 千帆大模型 · ERNIE 系列 | `BAIDU_WENXIN_API_KEY` / `BAIDU_WENXIN_SECRET_KEY` |
| 邮件导出发件箱 | —— | `MAIL_ACCOUNT` / `MAIL_AUTH_CODE` |

PowerShell 设置示例（对当前用户永久生效）：

```powershell
setx BAIDU_OCR_API_KEY       "你的Key"
setx BAIDU_OCR_SECRET_KEY    "你的Secret"
setx MAIL_ACCOUNT            "yourname@163.com"
setx MAIL_AUTH_CODE          "邮箱设置里生成的SMTP授权码（不是登录密码）"
```

设置完**重开 PowerShell 再启动**（setx 对已开窗口不生效）。多数服务有免费额度，超量会报配额错误。

## 十分钟走通全流程

> 界面是按 4 英寸触摸屏整机设计的：没有键盘输入，文字一律通过**拍照（手写 OCR）**、**录音（语音识别）**或**扫二维码**录入。凡是下面提到「扫码」的地方，用任意二维码生成器把对应文字做成二维码，对着摄像头点「拍照」即可。

1. **设置**（主菜单第 4 键）：收件邮箱、WiFi 名称、WiFi 密码三项，可以直接在右侧输入框里填，也可以点左侧对应按钮进入摄像头页扫码录入；点「保存」后邮箱写入 `data/case.yaml`，WiFi 名称 / 密码只存在内存里并立即尝试连接（重启应用需重填，不连 WiFi 可留空）
2. **研学笔记**（第 1 键）→「新建笔记」：点「笔记标题」给笔记起名（拍照或录音）；点「新建关键词」后**拍照**（或录音）输入一个关键词，比如展板上的「天津古文化街」——应用调 OCR 识别文字，大模型流式生成讲解正文
3. 新关键词的配图先是占位图：**点右侧配图区域**再拍一张，就成了这条关键词的配图（存到 `data/img/`）。多录几个关键词，一篇笔记就攒起来了；左侧点关键词切换正文与配图
4. **实时问答**（第 2 键）：点「开始录音」说出问题（如「灯火阑珊是什么意思」），说完点「结束录音」；或直接点「拍照」拍下手写的问题。识别后大模型流式作答，「历史」里可回看
5. **录课整理**（第 3 键）→ 新建课程：摄像头页会要求**扫一个内容为课程录像 mp4 直链 URL 的二维码**，扫到后视频开始播放，同时提交云端转写（需要几分钟）。之后点「提问」：转写未完成时按钮显示「正在转写」，稍后再点；完成后拍照或录音提出问题，大模型会在文稿里找出相关段落对应的时间点
6. **导出**：研学笔记页点「导出笔记」进入导出模式（按钮变为「导出模式」），再点列表里要导出的那篇笔记，整篇笔记（HTML + 内嵌图片）就从发件邮箱发到设置里的收件邮箱；按钮显示「导出成功」/「导出失败」，再点一次按钮退出导出模式

所有数据统一在仓库根的 `data/` 目录里：`data/case.yaml`（文字）与 `data/img/`（配图），备份整个 `data/` 即全量备份。

## 常见问题

- **启动报 `ModuleNotFoundError`**：先确认是通过 `script/launch.ps1` 启动（它会激活 venv 并锚定仓库根）；手动跑则需先在仓库根 `.\venv\Scripts\activate`
- **pyaudio 安装失败**：它是语音依赖，Windows 下偶尔没有现成轮子；`pip install pipwin` 后 `pipwin install pyaudio`，或到 PyPI 找对应 Python 3.9 的非官方轮子
- **API 报 110 / 111（Access token invalid / 过期）**：环境变量没设置或填错；重新 setx 后重开窗口
- **API 报 17（Open api daily request limit reached）**：当日免费额度用完，次日恢复或购买额度
- **拍照没反应 / 识别为空**：确认图片清晰、光线充足；手写体尽量工整
- **导出邮件收不到 / 显示「导出失败」**：查垃圾箱；确认 `MAIL_ACCOUNT` 是 163 邮箱、`MAIL_AUTH_CODE` 是 SMTP 授权码而非登录密码，且邮箱设置里已开启 SMTP 服务；具体报错看启动脚本的 PowerShell 窗口
- **主界面 WiFi 图标显示未联网但网络正常**：图标每 2 秒检测一次能否在 2 秒内打开 `https://www.baidu.com`，和设置页填的 WiFi 无关；代理、防火墙或访问百度慢都会导致误报

## 下一步

- [architecture.md](architecture.md)：模块职责、数据流与 `case.yaml` 结构，想二开先看这个

---

## English

What it is: a research-trip notes app — snap a board (handwriting OCR + LLM writes the note with your photo), ask by voice, transcribe lecture videos by URL, export notes via email.

Install: ASCII-only path; right-click-run `script/install.ps1` (venv + deps), then `script/launch.ps1`. Credentials (the only barrier): create one app per Baidu service (handwriting OCR / speech recognition / file transcription / ERNIE) plus an SMTP mailbox, then `setx` the five env-var pairs — mapping table above; reopen PowerShell after `setx`.

The UI targets a 4-inch touchscreen device with no keyboard: text is entered by photo (handwriting OCR), voice, or by scanning a QR code with the camera. 10-minute walkthrough: Settings (type or QR-scan the receiving mailbox; Wi-Fi fields are optional and kept in memory only) → Notes (new note, photograph or speak keywords; tap the image area to take the keyword's photo) → QA (tap "start recording", speak, tap again; or photograph a written question) → Lectures (new course asks you to scan a QR code containing the mp4 URL; the transcript is checked when you tap "ask" — it shows "transcribing" until done) → export: tap "导出笔记" to enter export mode, then tap a note to mail it. Data lives in the repo-root `data/` folder (`case.yaml` + `img/`); back up the folder and you have everything. Troubleshooting: error 110/111 = bad credentials, 17 = daily quota, missing pyaudio → `pipwin install pyaudio`, exported mail → check spam folder and that `MAIL_AUTH_CODE` is the SMTP authorization code (not the login password).

