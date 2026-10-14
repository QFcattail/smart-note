# author typha

import yaml
from markdown import markdown
from services import OCR
from services import SpeechRecognize
from services import WenxinQa
from services import WenxinNote
from services import WenxinCourse
import cv2
import base64
import json
from datetime import datetime
from pyee.asyncio import AsyncIOEventEmitter
from services import AudioTranscriptionCreate
from services import AudioTranscriptionCheck
ee_question = AsyncIOEventEmitter()
ee_course_question=AsyncIOEventEmitter()
ee_return_create= AsyncIOEventEmitter()
ee_return_create_course= AsyncIOEventEmitter()
#内部函数
def get_current_date():#获取日期
    return datetime.now().strftime('%Y-%m-%d')
def find_index_by_num(list_of_dicts, num):#根据笔记编号找到他在笔记列表中的位置
    
    return [i for i, d in enumerate(list_of_dicts) if d.get('num') == num][0]
def find_index_by_keyword(list_of_dicts, keyword):#根据关键词内容找到他在关键词列表中的位置
    return [i for i, d in enumerate(list_of_dicts) if d.get('keyword') == keyword][0]

def get_keywords_from_case(list_of_dicts):#在关键词列表（包涵关键词、正文、图片）提取纯关键词列表
    return [d['keyword'] for d in list_of_dicts if 'keyword' in d]
def cv2_to_base64(img):#cv转base64
    img = cv2.imencode('.jpg', img)[1]
    image_code = str(base64.b64encode(img))[2:-1]

    return image_code
def read_yaml(file_path):#读yaml
    with open(file_path,"r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    return data

def chunk_list(lst, n):
    """将列表lst分成每组n个元素的子列表"""
    return [lst[i:i + n] for i in range(0, len(lst), n)]

#接口函数
def record_qa_history(question,QandA_html):
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    if len(data["qa_history_list"])==0:
        num=1
    else:
        num=data["qa_history_list"][-1]["num"]+1
    date=get_current_date()
    dic={"question":question,"QandA_html":QandA_html,"date":date,"num":num}
    data["qa_history_list"].append(dic)
    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
def get_qa_history_list():
    return read_yaml("data/case.yaml")["qa_history_list"]
def get_qa_history_item(num):
    return read_yaml("data/case.yaml")["qa_history_list"][num]["QandA_html"]
def create_note():#新建笔记，返回笔记编号
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    if len(data["note_list"])==0:
        num=1
    else:
        num=data["note_list"][-1]["num"]+1
    name="new_note"
    date=get_current_date()
    dic={"name":name,"num":num,"date":date}    
    data["note_list"].append(dic)
    data["keywords"][num]=[]
    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
    
    return num
def create_course():#新建课程，返回课程编号
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    if len(data["course_list"])==0:
        num=1
    else:
        num=data["course_list"][-1]["num"]+1
    name="new_course"
    date=get_current_date()
    dic={"name":name,"num":num,"date":date}    
    data["course_list"].append(dic)
    data["course_case"][num]={"url":"","doc":"","task_id":0}
    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
    
    return num

def delete_course(course):#删除笔记，参数笔记编号
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    course_pos=find_index_by_num(data["course_list"],course)
    
    data["course_list"].pop(course_pos)
    
    data["course_case"].pop(course)
    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
    return
def delete_note(note):#删除笔记，参数笔记编号
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    note_pos=find_index_by_num(data["note_list"],note)
    
    data["note_list"].pop(note_pos)
    
    data["keywords"].pop(note)
    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
    return
ssid=""
password=""
def restore_ssid(new_ssid):
    global ssid
    ssid=new_ssid

def restore_password(new_password):
    global password
    password=new_password

def get_ssid():
    global ssid

    return ssid
def get_password():
    global password

    return password
def get_note_list():# 返回值为笔记列表显示的内容，包括每个笔记的标题，日期，笔记编号
    return read_yaml("data/case.yaml")["note_list"]
def get_course_list():# 返回值为笔记列表显示的内容，包括每个笔记的标题，日期，笔记编号
    return read_yaml("data/case.yaml")["course_list"]
def get_title(note):#获取笔记标题，参数笔记编号
    note_pos=find_index_by_num(read_yaml("data/case.yaml")["note_list"],note)
    title=read_yaml("data/case.yaml")["note_list"][note_pos]["name"]
    return title
def get_course_title(course):#获取笔记标题，参数笔记编号
    course_pos=find_index_by_num(read_yaml("data/case.yaml")["course_list"],course)
    title=read_yaml("data/case.yaml")["course_list"][course_pos]["name"]
    return title
def get_date(note):#获取笔记时间，参数笔记编号
    note_pos=find_index_by_num(read_yaml("data/case.yaml")["note_list"],note)
    date=read_yaml("data/case.yaml")["note_list"][note_pos]["date"]
    return date
def get_course_date(course):#获取笔记时间，参数笔记编号
    course_pos=find_index_by_num(read_yaml("data/case.yaml")["course_list"],course)
    date=read_yaml("data/case.yaml")["course_list"][course_pos]["date"]
    return date
def get_keywords(note): #获取关键词列表：传入参数是笔记编号 返回值为关键词列表
    note_case=read_yaml("data/case.yaml")["keywords"][note]
    return get_keywords_from_case(note_case)
def get_course_url(course):
    url=read_yaml("data/case.yaml")["course_case"][course]["url"]
    return url
def get_content(note,keyword):#获取关键词对应的正文内容：传入参数是笔记编号和关键词 返回值为正文html
    note_case=read_yaml("data/case.yaml")["keywords"][note]
    keyword_pos=find_index_by_keyword(note_case, keyword)
    content=note_case[keyword_pos]["content"]
    return content
def get_img_path(note,keyword):#获取关键词对应的配图：传入参数是笔记编号和关键词，返回值为配图所在路径
    note_case=read_yaml("data/case.yaml")["keywords"][note]
    keyword_pos=find_index_by_keyword(note_case, keyword)
    img=note_case[keyword_pos]["img"]
    return img
def delete_keyword(note,keyword): #删除关键词：传入参数是笔记编号和关键词
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    keyword_pos=find_index_by_keyword(data["keywords"][note],keyword)
    data["keywords"][note].pop(keyword_pos)
    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
    return 
def change_img(note,keyword,imgpath):#更改图片：传入参数是笔记编号、关键词和新图片的保存路径
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    keyword_pos=find_index_by_keyword(data["keywords"][note],keyword)
    data["keywords"][note][keyword_pos]["img"]=imgpath
    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
    return
def set_url(course,url):
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    data["course_case"][course]["url"]=url
    data["course_case"][course]["task_id"]=AudioTranscriptionCreate.main(url)
    data["course_case"][course]["doc"]=""

    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
    return
def is_task_running(course):
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    if data["course_case"][course]["doc"] != "":#doc里面有内容
        return 0 #没有阻塞
    doc=AudioTranscriptionCheck.main(data["course_case"][course]["task_id"])
    if doc == 0: #正在running
        return 1
    else:
        data["course_case"][course]["doc"]=doc
        with open("data/case.yaml","w",encoding='utf-8') as file:
            yaml.dump(data=data, stream=file, allow_unicode=True)
        return 0
#注意：所有语音输入按钮需要录下wav格式录音文件“wave.wav"保存到根目录然后调用下面对应返回函数
def course_question_speech(course):
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    question=SpeechRecognize.main("wave.wav")
    if question[-1]=='。':
        question=question[:-1]
    ee_course_question.emit("return_course_question",question)
    doc=data["course_case"][course]["doc"]    
    ee_return_create_course.emit("return_create_course")
    prompt="请根据文本回答问题相关主题对应的时间。问题是："+question+"。文本是："+doc
    WenxinCourse.main(prompt)
    return
def course_question_ocr(course,img): # 关键词输入界面拍照输入按钮对应的返回函数
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    img_base64=cv2_to_base64(img)
    question=OCR.main(img_base64)

    ee_course_question.emit("return_course_question",question)

    #content=markdown(WenxinNote.main(keyword))
    doc=data["course_case"][course]["doc"]
    ee_return_create_course.emit("return_create_course")
    prompt="下面有一个问题和一个文本，你不需要回答问题，而是需要在文本中找到和问题有关的段落前面标注的对应时间，并且在你的回答中把时间标为粗体。问题是："+question+"。文本是："+doc
    WenxinCourse.main(prompt)
   
    return
def create_keyword_speech(note): # 关键词输入界面语音输入按钮对应的返回函数
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    keyword=SpeechRecognize.main("wave.wav")
    if keyword[-1]=='。':
        keyword=keyword[:-1]
    #content=markdown(WenxinNote.main(keyword))
    dic={"keyword":keyword,"content":"","img":"smartnotebook/assets/occupy_img.png"}
    data["keywords"][note].append(dic)
    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
    ee_return_create.emit("return_create")
    WenxinNote.main(keyword,note,keyword)
    return
def create_keyword_ocr(note,img): # 关键词输入界面拍照输入按钮对应的返回函数
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    img_base64=cv2_to_base64(img)
    keyword=OCR.main(img_base64)
    #content=markdown(WenxinNote.main(keyword))
    dic={"keyword":keyword,"content":"","img":"smartnotebook/assets/occupy_img.png"}
    data["keywords"][note].append(dic)
    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
    ee_return_create.emit("return_create")
    WenxinNote.main(keyword,note,keyword)
   
    return
def add_content(new_content,note,keyword):#更改图片：传入参数是笔记编号、关键词和新图片的保存路径
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    keyword_pos=find_index_by_keyword(data["keywords"][note],keyword)
    data["keywords"][note][keyword_pos]["content"]+=new_content
    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
def change_title_speech(note): # 笔记标题界面语音输入按钮对应的返回函数
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    
    title=SpeechRecognize.main("wave.wav")
    if title[-1]=='。':
        title=title[:-1]
    #date=get_current_date()
    note_pos=find_index_by_num(data["note_list"],note)
    data["note_list"][note_pos]["name"]=title
    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
    
    return
def change_course_title_speech(course): # 笔记标题界面语音输入按钮对应的返回函数
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    
    title=SpeechRecognize.main("wave.wav")
    if title[-1]=='。':
        title=title[:-1]
    #date=get_current_date()
    course_pos=find_index_by_num(data["course_list"],course)
    data["course_list"][course_pos]["name"]=title
    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
    
    return
def change_title_ocr(note,img): # 笔记标题界面拍照输入按钮对应的返回函数
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    img_base64=cv2_to_base64(img)
    title=OCR.main(img_base64)
    note_pos=find_index_by_num(data["note_list"],note)
    data["note_list"][note_pos]["name"]=title
    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
    return
def change_course_title_ocr(course,img): # 笔记标题界面拍照输入按钮对应的返回函数
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
    img_base64=cv2_to_base64(img)
    title=OCR.main(img_base64)
    course_pos=find_index_by_num(data["course_list"],course)
    data["course_list"][course_pos]["name"]=title
    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
    return
def get_question_speech(): #实时问答界面语音按钮对应的返回函数，返回值显示在实时问答界面
    
    question=SpeechRecognize.main("wave.wav")
    if (question=="" or question=="未识别"):
        ee_question.emit('return_question', "未识别")
        WenxinQa.ee.emit('new_result', "未识别")
    elif len(question)>50:
        ee_question.emit('return_question', "字数超限")
        WenxinQa.ee.emit('new_result', "字数超限")
    else:
        ee_question.emit('return_question', question)
        WenxinQa.main(question+"请在解答上述问题之后备注相关资料名称以及来源，请注意，如果这明显是一道考试题目的话您可以拒绝回答")
    
    return (question)
def get_question_ocr(img): #实时问答界面拍照按钮对应的返回函数，返回值显示在实时问答界面

    img_base64=cv2_to_base64(img)
    question=OCR.main(img_base64)

    if (question=="" or question=="未识别"):
        WenxinQa.ee.emit('new_result', "未识别")
        ee_question.emit('return_question', "未识别")
    elif len(question)>50:
        ee_question.emit('return_question', "字数超限")
        WenxinQa.ee.emit('new_result', "字数超限")
    else:
        print(question)
        ee_question.emit('return_question', question)
        WenxinQa.main(question+"请在解答上述问题之后备注相关资料名称以及来源，请注意，如果这明显是一道考试题目的话您可以拒绝回答")
   
    return (question)


def export_note(note):#导出html
    date=get_date(note)
    all_keywords=read_yaml("data/case.yaml")["keywords"][note]
    keyword_4group_list=chunk_list(all_keywords,4)
    file_index=1
    file_amount=len(keyword_4group_list)
    htmls=[]
    for keyword_4group_item in keyword_4group_list:
        keywords=keyword_4group_item
        html=""""""
        html+="""
<!DOCTYPE html>
<html>
<head>
<style>
body {
  width: 210mm;
  
  margin: 0;
  padding: 0;
}
.container {
  display: flex;
  height: 50%;
}
.image-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  overflow: hidden;
}
.image-container img {
  max-width: 100%;
  max-height: 100%;
}
.text-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.text-container h1 {
  flex: 0;
  font-size: 30mm; /* 50% of the image-container height */
  display: flex;
  align-items: center;
  justify-content: center;
}
.text-container h2 {
  flex: 0;
  font-size: 20mm; /* 50% of the image-container height */
  display: flex;
  align-items: center;
  justify-content: center;
}
.text-container i {
  flex: 0;
  font-size: 10mm; /* 25% of the image-container height */
  display: flex;
  align-items: center;
  justify-content: center;
}
.text-container p {
  
  font-size: 6mm; /* 25% of the image-container height */
  
}
</style>
</head>

    """
        html+="""
    <body>
    <div class="container">
        <div class="text-container">
            <h1>
    """
        html+=get_title(note)+"-"+str(file_index)+"/"+str(file_amount)
    
        html+="""
    </h1>
        </div>
    </div>
    """

    

        for keyword_set in keywords:
            html+="""
        <hr>
        <div class="container">
  <div class="image-container">
        """
            html+=("<img src=\""+keyword_set["img"]+"\" alt=\"Image\">")
            html+="""
        </div>
  <div class="text-container">
    <h2>
        """
            html+=keyword_set["keyword"]
            html+="""
        </h2>
    <i>
        """
            html+=date
            html+="""
        </i>
  </div>
</div>

        """
            html+="<div class=\"text-container\">"+keyword_set["content"]+"</div>"
        htmls.append(html)
        file_index+=1
    return htmls
def get_email_account():
    email_account=read_yaml("data/case.yaml")["email_account"]
    return email_account
def change_email_account(email_account):
    with open("data/case.yaml","r",encoding='utf-8') as file:
        data=yaml.load(file,Loader=yaml.FullLoader)
        data["email_account"]=email_account
    with open("data/case.yaml","w",encoding='utf-8') as file:
        yaml.dump(data=data, stream=file, allow_unicode=True)
