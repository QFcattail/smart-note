# smart-notebook — A Pocket AI Q&A Learning Device, in Software

> **In one sentence**: the complete software of a pocket AI Q&A learning device — photograph a board or handout and it becomes an illustrated note via handwriting OCR plus an LLM; ask questions by voice; scan a QR code holding a lecture-video URL to transcribe it and locate answers by timestamp; export notes by email.
>
> 拍照成笔记、语音问答、录课转写整理、邮件导出——一台随身答疑学习机的全部软件。

A prize-winning 2023–2024 youth science-innovation project. Conceived right after ChatGPT landed: the author was juggling physics and biology olympiads, had many niche questions, and phones were banned at school — so here is a device that **answers anywhere, turns questions into a knowledge base, and recommends further reading** (in hindsight, the same idea as RAG and memory mechanisms). The physical product is a Raspberry Pi 3B+ with a 4-inch touchscreen, camera and microphone in a 3D-printed / laser-cut shell; **this repository is its entire software** (PyQt5), which also runs directly on Windows.

![Product form: 3D-printed shell with a 4-inch touchscreen](docs/assets/product-form.webp)

| Hand-drawn exploded view | Hardware teardown (Pi 3B+ · UPS battery · camera · mic · switch) |
| --- | --- |
| ![Hand-drawn exploded view](docs/assets/hardware-exploded.png) | ![Hardware teardown](docs/assets/hardware-teardown.png) |

The main menu has four entries backing three feature lines over one shared "input → LLM understanding → output" backbone:

![System architecture](docs/assets/system-architecture.svg)

- **Real-time QA**: photo / voice → ERNIE semantic understanding → concise answer + further reading
- **Note composing**: classroom keywords → LLM-supplied material → an illustrated HTML note
- **Lecture organizing**: lecture video → timestamped transcript → jump to video positions by topic or question

All AI capabilities come from Baidu AI Cloud (ERNIE / handwriting OCR / ASR / file transcription); no local models.

---

## Table of Contents

- [What It Does](#what-it-does)
- [Quick Start (15 min)](#quick-start-15-min)
- [Architecture at a Glance](#architecture-at-a-glance)
- [Repository Layout](#repository-layout)
- [Beginner Roadmap](#beginner-roadmap)
- [Key Concepts](#key-concepts)
- [Design Notes](#design-notes)
- [Known Limitations](#known-limitations)
- [Docs & Code Conventions](#docs--code-conventions)
- [Team & Acknowledgements](#team--acknowledgements)
- [License](#license)

---

## What It Does

![Main menu: Notes / QA / Lectures / Settings](docs/assets/ui-main.png)

On a study trip: photograph an exhibit board; handwriting OCR extracts the keyword and an ERNIE model streams an explanatory paragraph; tap the image area to take a photo of the exhibit as its illustration — a few snaps and the note assembles itself.

![Note-composing flow](docs/assets/note-flow.svg)

Questions written on scratch paper are photographed, or spoken after tapping "start recording"; answers stream in sentence by sentence and are kept in a local history. Back in class, scan a QR code containing the mp4 URL of a lecture recording: the video plays while the cloud transcribes it with timestamps, and later questions are answered with the matching positions such as "18 min 32 s". Finally, export mails the whole note (HTML with embedded images) to the mailbox set in Settings.

The device has no keyboard: all text is entered by photo (handwriting OCR), voice, or QR code — a deliberate choice for classrooms where speaking is disruptive and outdoor trips where typing is impractical.

Measured before the project defense: ~**98%** handwriting-OCR accuracy across fonts, classical-Chinese rare characters included.

## Quick Start (15 min)

1. Windows 10/11 + Python 3.9, repo in an **ASCII-only path**
2. Right-click `script/install.ps1` → "Run with PowerShell" (creates venv, installs deps)
3. Create one app per service in the [Baidu AI Cloud console](https://console.bce.baidu.com/) and set the Key/Secret pairs as environment variables (mapping table and `setx` examples in [`docs/getting-started.md`](docs/getting-started.md), Chinese)
4. Right-click `script/launch.ps1` to start → fill the receiving mailbox in "设置" (Settings) → create your first note in "研学笔记" (a camera is required; a laptop webcam works)

Full walkthrough and troubleshooting: [`docs/getting-started.md`](docs/getting-started.md) (Chinese).

## Architecture at a Glance

```
photo / voice ──> OCR.py / SpeechRecognize.py ──> text keyword
                      │
                      ▼  WenxinNote (ERNIE): streams HTML content
case.yaml <── function.py (business hub: notes / courses / keywords / QA CRUD)
   │  │
   │  └─ export: mailUtils.py (SMTP, HTML with embedded images)
   │
   ├─ QA: OCR / SpeechRecognize → WenxinQa → qa_history_list
   └─ lecture: QR-scanned URL → AudioTranscriptionCreate (submit job)
               → AudioTranscriptionCheck (queried on "ask"; transcript stored in course_case)
               → WenxinCourse (locate timestamps for the question)
```

Module responsibilities, data flows and the `case.yaml` schema: [`docs/architecture.md`](docs/architecture.md) (Chinese).

## Repository Layout

```
smartnotebook/                  the application package
  main.py / app.py              entry point and QApplication (script/launch.ps1 runs python smartnotebook\main.py)
  ui/                           frontend: one *ui.py (Qt Designer layout) + *uic.py (logic) pair per page
    mainui.py                   main menu (notes / QA / lectures / settings)
  core/                         backend: business and data
    function.py                 business hub: case.yaml I/O, data management, pipelines
  services/                     backend: external-service wrappers
    OCR.py / SpeechRecognize.py / AudioTranscription*.py   Baidu AI (handwriting / ASR / transcription)
    Wenxin*.py                  ERNIE chat wrappers (single / note / course / QA / flow)
    mailUtils.py / wifiUtils.py SMTP export / connectivity check
  assets/                       UI icons and placeholders
data/                           all business data: case.yaml (six keys) + img/ (runtime photos)
script/                         install.ps1 (setup) / launch.ps1 (launcher, anchors to repo root)
requirements.txt                dependency list (read by install.ps1)
docs/                           getting-started / architecture / assets (diagrams, hardware photos)
```

## Beginner Roadmap

1. **Get it running** — "Quick Start" here plus the credentials section of [`docs/getting-started.md`](docs/getting-started.md) (without keys nothing works; that is the only barrier)
2. **Walk the three flows** — snap a note, voice QA, lecture transcription, then email export (same doc)
3. **Understand the data** — [`docs/architecture.md`](docs/architecture.md): six-key schema, three data flows; everything lives in the `data/` folder (`case.yaml` + `img/`)
4. **Hack it** — each hand-written module has a sibling `.doc.md`; start from `core/function.py`; to swap the LLM read `services/WenxinSingle.py`; UI logic lives in `ui/`

## Key Concepts

| Term | Meaning |
| --- | --- |
| Note | basic unit, id `num`, holds keyword entries |
| Keyword entry | `{keyword, content, img}`: keyword + generated HTML + image path |
| Course | lecture unit: `{doc, task_id, url}` — transcript / job id / video URL |
| QA history | `{question, QandA_html, date, num}` rendered as HTML |
| data/ | the single data folder: `case.yaml` (six keys) + `img/` photos; backing up the folder backs up everything |
| Environment variables | all 5 credential pairs via `os.environ`; no secrets in code |

## Design Notes

For anyone building something similar — each point maps to a place in the code:

- **Pick the input method first**: speaking is disruptive in class and typing is slow, so handwriting OCR is primary and voice secondary; settings with special characters (Wi-Fi passwords) are entered by QR code instead of a hard-to-build soft keyboard (`ui/*inputuic.py`)
- **All compute in the cloud**: a Raspberry Pi can't run an LLM, so OCR / ASR / transcription / ERNIE are Baidu AI Cloud REST calls; the device only captures, renders and stores. One file per API — switching providers only touches `services/`
- **Streaming to cut waiting**: LLM answers are read with aiohttp streaming and pushed to the UI via pyee events, one sentence at a time (`services/Wenxin*.py`)
- **One model, one prompt per scenario**: QA, note expansion and lecture timestamp lookup prompts all live in `core/function.py`
- **Anti-dependency, not a homework solver**: questions over 50 characters are rejected, and the QA prompt tells the model to decline obvious exam questions (`core/function.get_question_*`)
- **The database is one YAML file**: `data/case.yaml` plus an image folder — readable by hand, backed up by copying
- **Layout and logic in separate files**: each page was sketched on paper first (widgets, navigation, fields read and written), then split into `*ui.py` (Qt Designer layout) and `*uic.py` (event logic)

## Known Limitations

- Depends on Baidu AI Cloud APIs and network; free quotas are limited (error 17 when exceeded)
- LLM calls target the 2023–2024 Qianfan v1 API (`wenxinworkshop/chat/completions`); Baidu has since introduced a v2 API and is retiring older models — if LLM calls fail, update the endpoint and auth in `services/Wenxin*.py` per the current Qianfan docs
- No follow-up questions; lecture questions put the whole transcript into one prompt, so long videos exceed the model's input limit
- Voice recognition is noise-sensitive; OCR depends on photo quality and essentially cannot read math formulas or symbols
- Export hardcodes 163 SMTP (SSL 465); other providers need a small edit in `mailUtils.py`
- Setup / launch scripts are Windows PowerShell only; the original device ran on a Raspberry Pi 3B+ (Raspberry Pi OS) — on Linux, run `pip install -r requirements.txt`, then `python smartnotebook/main.py` from the repo root

## Docs & Code Conventions

- Every hand-written code file has a sibling `<filename>.doc.md` (Chinese first, then English): responsibility, key functions, pitfalls
- Qt-Designer-exported `*ui.py` layout files are documented collectively in `docs/architecture.md` (naming convention section) instead of per-file
- Process / iteration documents are not kept in this repository
- Credentials always come from environment variables (names in getting-started); no hardcoded secrets

## Team & Acknowledgements

A project from Beijing Changping No. 2 High School (2023–2024).

| Member | Role |
| --- | --- |
| Cheng Qianhe (水烛 / typha) | concept, software and architecture, led the iterations |
| Qiu Jiacheng | hardware: 3D-printed enclosure, power supply |
| Li Shaoyun | surveys, project defense and outreach |
| Zhang Jiayi | joined for the National Youth Science Popularization Innovation Competition |

Advisors: Yang Jing, Wang Jifei, Tian Junxin. Thanks to the school's robotics club and to all the classmates and teachers who took part in the surveys and trials.

Demo video, hardware iterations and the research report: [project page](https://profile.typha.top/exp/notebook.html) (Chinese).

## License

[MIT](LICENSE)
