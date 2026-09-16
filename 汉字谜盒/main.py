import json
import logging
import os.path
from datetime import datetime
from typing import Any
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel
from pyexpat.errors import messages
from starlette.responses import FileResponse, JSONResponse
from starlette.staticfiles import StaticFiles


#创建fastapi
app = FastAPI(title="汉字谜盒")
#静态挂载
app.mount("/static",StaticFiles(directory="static"),name="static")

#创建与AI大模型交互的客户端对象
client = OpenAI(api_key='sk-11ab1e1d0eed4f61bc854693b3ccf9de', base_url="https://api.deepseek.com")


#日志记录:配置日志信息;记录时间、文件名、行号、日志级别和日志内容
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')

#异常处理器；统一处理初五
@app.exception_handler(Exception)
async def exception_handler(request, exc):
    logging.error(f"异常信息： {request.method} {request.url}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"message": "服务器内部出错"},
    )


#根据session_id获取文件名
def get_session_file_name(session_id):
    return f"sessions/{session_id}.json"

#系统提示词
system_prompt = """
你是一位"猜汉字"游戏的主持人。你的任务是引导用户进行猜汉字游戏，规则如下：
## 游戏规则
1. **角色定位**：你是出题方，用户是猜题方。
2. **出题方式**：随机出一道经典字谜（如"一口咬掉牛尾巴"），你需要根据谜面提示猜出对应的汉字，AI会根据你的回答给出相应的提示，并给出最终的答案。
3. **线索数量**：每轮游戏给出 3-5 条线索，由易到难逐步递进。
4. **线索类型**（可混合使用以下方式）：
   - **字形线索**：描述汉字的偏旁部首、笔画数、结构（左右/上下/半包围等）。
   - **字义线索**：描述该汉字的含义或用法。
   - **组词线索**：给出含有该字的常见词语。
   - **谜面线索**：用谜语的方式描述该字（如"一口咬掉牛尾巴"= 告）。
   - **语境线索**：给出一句包含该字的例句或成语。
5. **互动流程**：
   - 先给出第 1 条线索，等待用户回答。
   - 若用户猜对，则公布答案并给予鼓励，询问是否继续下一轮。
   - 若用户猜错，则给出第 2 条线索，继续等待。
   - 依此类推，若所有线索用完用户仍未猜对，则公布答案并解释。
6. **难度控制**：
   - 第 1 轮线索给出后，用户需自行猜测，不要主动透露答案。
   - 每条新线索应比上一条更明显。
   - 最后一条线索应让答案几乎一目了然。
7. **题目选择**：选择常用汉字（避免生僻字），字数笔画在 3-20 画之间，适合一般中文使用者。
8. **反馈风格**：
   - 猜对时：热情鼓励，如"太棒了！就是'X'字！"
   - 猜错时：温和引导，如"还不是哦，再想想～给你下一条线索。"
   - 公布答案时：简要解释该字的字形、字义和常见用法。
## 互动约束
- 每次只给出一条线索，不要一次性给出所有线索。
- 用户每次回答后，先判断对错再决定下一步动作。
- 如果用户主动请求"跳过"或"公布答案"，则直接公布。
- 如果用户请求"再来一题"，则开始新一轮游戏。
- 如果用户请求调整难度（如"简单一点""难一点"），相应调整汉字的选择范围。
## 对话模板
**出题**：
> 🎯 第 X 条线索：[线索内容]
> 你猜这是什么字？
**猜对**：
> ✅ 太棒了！答案就是"X"！[简要解释]
> 要继续下一轮吗？
**猜错**：
> ❌ 还不是哦～再给你一条线索：
> 🎯 第 X 条线索：[线索内容]
**公布答案**：
> 📖 答案是"X"字。[解释字形字义和用法]
## 开始方式
当用户说"开始""玩""猜字"等意图词时，正式开始第一轮游戏。
当用户没有明确开始时，先简单介绍游戏规则并询问是否开始。
"""



#创建保存目录
if not os.path.exists("sessions"):
    os.mkdir("sessions")

@app.get("/")
async def root()->FileResponse:
    logging.info("访问项目首页")
    return FileResponse("static/index.html")#返回文件响应



# @app.get("/api/sessions")
# async def root()->FileResponse:
#     print("访问项目首页")
#     return FileResponse("static/index.html")#返回文件响应

#新建会话
def generate_session_id():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

#响应数据模型
class ApiResponse(BaseModel):
    code:int
    message:str
    data:Any

#响应数据模型
class ChatRequest(BaseModel):
    session_id:str
    message:str



@app.post("/api/sessions")
def create_session():
    logging.info("创建会话")
    #生成会话标识
    session_id = generate_session_id()
    #创建会话消息，保存到文件
    session_data={
    "current_session":session_id,
    "messages":[]
    }
    with open(get_session_file_name(session_id), "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=4)
    return ApiResponse(code=200, message="会话创建成功", data=session_id)

#与AI交互
@app.post("/api/chat")
def chat_session(request:ChatRequest):
    logging.info(f"与AI交互:{request.session_id},{request.message}")
    #交互逻辑：加载json文件中的会话数据
    session_path = get_session_file_name(request.session_id)
    if not os.path.exists(session_path):
        return ApiResponse(code=404, message="会话不存在", data=None)
    with open(session_path, "r", encoding="utf-8") as f:
        session_data = json.load(f)

    #构建AI大模型交互的信息
    messages =[{"role":"system","content":system_prompt}]
    for message in session_data["messages"]:
        messages.append(message)
    messages.append({"role":"user","content":request.message})
    #调用AI大模型
    logging.info(f"---->请求的会话信息{messages}")
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=messages,
        stream=False,
        temperature=1.5#模型生成结果随机性和多样性
    )

    #获取响应的数据
    ai_response = response.choices[0].message.content
    logging.info(f"---->AI的响应{ai_response}")
    #更新列表的消息
    messages.pop(0)
    messages.append({"role":"assistant","content":ai_response})#更新列表消息
    session_data["messages"]=messages#更新会话数据
    logging.info("---->更新后的会话数据",session_data)

    #保存会话信息到json中
    with open(session_path, "w", encoding="utf-8") as f:
        json.dump(session_data,f,ensure_ascii=False,indent=4)

    #返回数据
    return ApiResponse(code=200,message="与AI交互成功",data=ai_response)


#获取会话列表
@app.get("/api/sessions")
def get_sessions()->ApiResponse:
    logging.info("获取会话列表")
    #h获取会话目录下的所有文件名
    session_files = os.listdir("sessions")
    #获取文件名的会话ID
    session_ids = [file.split(".")[0] for file in session_files]
    session_ids.sort(reverse=True)
    #返回数据
    return ApiResponse(code=200, message="会话列表获取成功", data=session_ids)

@app.get("/api/sessions/{session_id}")
def get_session(session_id:str)->ApiResponse:
    logging.info(f"获取指定会话详情:{session_id}")
    #获取会话文件路径
    session_path = get_session_file_name(session_id)
    #检查会话文件是否存在
    if not os.path.exists(session_path):
        return ApiResponse(code=404, message="会话不存在", data=None)
    #读取会话文件内容
    with open(session_path, "r", encoding="utf-8") as f:
        session_data = json.load(f)
    #返回数据
    return ApiResponse(code=200, message="会话详情获取成功", data=session_data)


#删除会话
@app.delete("/api/sessions/{session_id}")
def delete_session(session_id:str)->ApiResponse:
    logging.info(f"删除指定会话:{session_id}")
    #获取会话文件路径
    session_path = get_session_file_name(session_id)
    #检查会话文件是否存在
    if not os.path.exists(session_path):
        return ApiResponse(code=404, message="会话不存在", data=None)
    #删除会话文件
    os.remove(session_path)
    #返回数据
    return ApiResponse(code=200, message="会话删除成功", data=None)



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app,host='0.0.0.0',port=8001,access_log=True)#日志开关