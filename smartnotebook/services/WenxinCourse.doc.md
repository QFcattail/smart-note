# WenxinCourse.py — 文心千帆对话封装（录课时间定位）

骨架同 `WenxinSingle.py`，签名 `(prompt)`：`function.course_question_ocr/speech` 把用户问题和整份转写文稿（`course_case.<num>.doc`）拼进 prompt，要求模型找出与问题相关段落前标注的时间并加粗；结果经 `new_course_result` 事件流式推给课程页，不落盘。凭据 `BAIDU_WENXIN_*`。共用坑点见 `WenxinSingle.doc.md`。

- 整份文稿一次性进 prompt，长视频会超出模型输入长度

---

## English

Same skeleton as `WenxinSingle.py`, signature `(prompt)`: `function.course_question_ocr/speech` puts the user's question plus the whole transcript (`course_case.<num>.doc`) into the prompt and asks the model to return the (bolded) timestamps of the relevant passages; results stream to the course page via `new_course_result` events and are not persisted. Credentials `BAIDU_WENXIN_*`; shared pitfalls in `WenxinSingle.doc.md`. The whole transcript goes into one prompt, so long lectures exceed the model's input limit.
