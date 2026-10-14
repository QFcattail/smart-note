# smartnotebook 包说明（组件 README）

本包是智能研学笔记的全部应用代码，按 **前端 ui / 业务 core / 外部服务 services** 三层组织。本文件只做速览；**详细的模块分工、数据流动与模块通讯机制见 [`../docs/architecture.md`](../docs/architecture.md)**。

## 包结构

```
smartnotebook/
  main.py / app.py     入口：QApplication + 主窗口调度（时钟 / WiFi 状态 / 页面切换）
  ui/                  前端：mainui + 10 对 *ui.py（Qt Designer 布局）/*uic.py（事件逻辑）
  core/                业务：function.py —— data/case.yaml 唯一读写者，流程编排
  services/            外部服务：OCR / 语音识别 / 转写 / 文心千帆 / SMTP 邮件 / WiFi 检测
  assets/              界面图标与占位图（按 __file__ 包内寻址）
```

## 调用链速览

```
main.py ──> ui/*uic.py（界面 + 线程调度）
                │  采集（拍照/录音）与用户输入
                ▼
          core/function.py ── 校验、拼 prompt、读写 data/case.yaml
                │
                ▼
          services/*（百度 AI / SMTP）── 无状态封装，凭据来自环境变量
                │
                └── 流式结果经 pyee 事件 / Qt 信号逐级回传界面渲染
```

## 通讯约定

- 界面窗口类自带 `pyqtSignal`（`conn` / `vedioconn` / `voiceconn`），daemon 线程算完 `emit` 回主线程
- `core/function.py` 用自定义信号（`ee_question` 等）向界面回报业务节点；出错时也发占位事件
- `services/Wenxin*.py` 用 `pyee.AsyncIOEventEmitter` 做流式逐字上屏
- 时钟与摄像头取景用 `QTimer`；联网检测是后台线程每 2 秒访问一次 baidu.com；转写状态不轮询，只在课程页点「提问」时查一次

## 规则与坑点

- 依赖方向 **ui → core → services**；写数据必须经 `core/function.py`（`data/case.yaml` 全量覆写、无锁，别从别处直接写）
- 界面图标在 `assets/`，代码用 `os.path.dirname(__file__)` 包内寻址；业务数据在仓库根 `data/`，**必须从仓库根启动**（`script/launch.ps1` 已处理）
- 用户拍照存 `data/img/`，与 `data/case.yaml` 一起构成全量数据

---

## English

All application code of smart-notebook, layered as frontend `ui/` / business `core/` / external `services/`. This is a quick map — the deep dive (module responsibilities, data flows, communication) lives in [`../docs/architecture.md`](../docs/architecture.md).

Call chain: `main.py` → `ui/*uic.py` (pages + thread scheduling) → `core/function.py` (validation, prompts, sole reader/writer of `data/case.yaml`) → `services/*` (stateless Baidu/SMTP wrappers, credentials from env vars); streaming results travel back via pyee events and Qt signals. Conventions: dependency direction `ui → core → services`; all writes go through `core`; icons resolve inside the package via `__file__`, business data lives in the repo-root `data/` folder — always start the app from the repo root (`script/launch.ps1` handles it).
