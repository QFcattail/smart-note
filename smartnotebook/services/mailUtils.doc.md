# mailUtils.py — SMTP 邮件导出

`send_email(note_current_num, html_contents)`：把笔记 HTML 逐封发出（长笔记分多封，主题带 `i/N`）；`send_email_item` 用 BeautifulSoup 扫出 `<img>`，图片转 MIME 内嵌（Content-ID 替换 src），正文+图一封信。

- 凭据读环境变量 `MAIL_ACCOUNT`（发件邮箱）/ `MAIL_AUTH_CODE`（SMTP 授权码，非登录密码）
- 服务器硬编码 `smtp.163.com:465`（SSL）；收件人来自 `case.yaml` 的 `email_account`（设置页保存）

## 坑点

- 换其他邮箱服务商要改 `smtplib.SMTP_SSL(...)` 一行与其授权码规则
- `img` 标签的 src 必须是本地可读路径（相对仓库根）；外链图不会被内嵌

---

## English

`send_email` mails a note's HTML (split into numbered parts when long); `send_email_item` scans `<img>` tags with BeautifulSoup, embeds images as MIME parts (Content-ID) and sends body + images in one message. Credentials from `MAIL_ACCOUNT` / `MAIL_AUTH_CODE` env vars; the server is hardcoded to `smtp.163.com:465` (SSL) — one line to change for other providers; recipients come from `case.yaml`'s `email_account`. Image src must be locally readable paths; remote URLs are not embedded.
