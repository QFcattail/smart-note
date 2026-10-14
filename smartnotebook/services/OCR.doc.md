# OCR.py — 百度手写文字识别封装

`main(payload)`：图片经 `cv2_to_base64`（function.py）编码后 POST `aip.baidubce.com/rest/2.0/ocr/v1/handwriting`，返回识别文本。

- 凭据：`API_KEY` / `SECRET_KEY` 读环境变量 `BAIDU_OCR_API_KEY` / `BAIDU_OCR_SECRET_KEY`；`get_access_token()` 用 client_credentials 换 token
- 调用方：`function.create_keyword_ocr` / `change_title_ocr` / `course_question_ocr`

## 坑点

- token 不缓存，每次识别都重新获取；高并发会撞频率限制（QPS）
- 手写体识别对拍摄角度与光线敏感，模糊图会返回空结果而不是报错

---

## English

Wrapper for Baidu handwriting OCR: `main(payload)` posts a base64 image to the handwriting endpoint and returns recognized text. Credentials come from `BAIDU_OCR_API_KEY` / `BAIDU_OCR_SECRET_KEY` env vars; `get_access_token()` exchanges them per call (not cached — mind QPS limits on bursts). Blurry photos return empty results rather than errors.
