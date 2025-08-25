# from database import *
from googleClient import *
from collections import defaultdict
from audio import *
import asyncio
from common import *
import json
messages = defaultdict(int)
project_client = None
agents_client= None
agent = None
thread = None
thread2 = None
temperature = 0.9
api_type = "azure"
api_version = "2024-12-01-preview"
engine = "gpt-4o"
model ="gpt-4o"

system_content = "Do not ask any clarifying questions."
max_retries = 5
timeout = 30
debug = "true"

agent_uri =  getKeyValue("agent-uri")
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    MessageDeltaChunk,   
    MessageRole,
    MessageDeltaTextUrlCitationAnnotation,
    MessageDeltaTextContent, 
)

def setupChat():
    global project_client
    global agents_client
    global agent
    global thread, thread2

    try:
        # await setup_openai_realtime()
        if project_client == None:
            project_client = AIProjectClient(endpoint=agent_uri, credential=DefaultAzureCredential())
        if agents_client == None:
            agents_client = project_client.agents
        if agent == None:
            agent = agents_client.get_agent("asst_58piOsPpG4mOb2CdVWZC9uPF")
        if thread == None:
            thread = agents_client.threads.create()
        if thread2 == None:
            thread2 = agents_client.threads.create()
    except  Exception as e:
        print(str(e))



@cl.on_window_message
async def window_message(message: str):
    try:
        first_key = next(iter(message))
        cl.user_session.set(first_key, message[first_key])

        if first_key == "mode":
            content = {"command":"mode","value":message[first_key],"status":"processing"}
            await cl.send_window_message(content)

        if first_key == "correlationId":
            cl.user_session.set("correlationId", message[first_key])
            # await temp()
    except Exception as ex:
        print(str(ex))
         
commands = [
    
    {"id": "Search", "icon": "globe", "description": "Find answers","persistent":"true"},
    {"id": "Project", "icon": "file-stack", "description": "Project mode","persistent":"true"},
    {"id": "Research", "icon": "school", "description": "Scholarly articles","persistent":"true"} ,    
     {"id": "Video", "icon": "school", "description": "Video","persistent":"true"} ,
    {"id": "Image", "icon": "school", "description": "Scholarly articles","persistent":"true"} ,
    {"id": "World News", "icon": "image", "description": "Image","persistent":"true"} 
]

@cl.on_chat_start
async def on_chat_start():

    try:
        filepath = "/tmp/tmp.txt"
        with open(filepath, 'w') as file:
            file.write('This file is saved in a new folder.\n')
            print("File written!")

            try:
                with open('tmp.txt', 'r') as file:
                    content = file.read()
                    print("file content " + content)
                    
            except FileNotFoundError:
                print("Error: File not found.")

    except Exception as e:
        print("exception while writing file " + str(e))

    global project_client,agents_client,agent,thread,thread2

    project_client = AIProjectClient(endpoint=agent_uri, credential=DefaultAzureCredential())
    agents_client = project_client.agents
    agent = agents_client.get_agent("asst_58piOsPpG4mOb2CdVWZC9uPF")
    thread = agents_client.threads.create()
    thread2 = agents_client.threads.create()

    await setup_openai_realtime()
    message_history = [{"role": "system", "content": system_content}]
    cl.user_session.set("message_history", message_history)

    content = {"command":"useremail","status":"processing"}
    await cl.send_window_message(content)

    content = {"command":"getreqlimits","status":"processing"}
    await cl.send_window_message(content)

    cl.user_session.set("mode","search")

    content =  "started"
    await cl.send_window_message(content)

    await cl.context.emitter.set_commands(commands)
    setupChat()

def checkForSessionVariables():

    try:
        project_client = cl.user_session.get("project_client")
        agents_client = cl.user_session.get("agents_client")
        agent = cl.user_session.get("agent")
        # logger = cl.user_session.get("logger")
        thread = cl.user_session.get("thread")
        thread2 = cl.user_session.get("thread2")
    except Exception as e:
        return False

    if project_client == None or agents_client == None or agent == None or  thread == None  or thread2 == None:
            return False

    return True


# os.environ["OAUTH_GOOGLE_CLIENT_ID"] = getKeyValue("google-client-id")
# os.environ["OAUTH_GOOGLE_CLIENT_SECRET"] = getKeyValue("google-auth-secret")
# os.environ["CHAINLIT_AUTH_SECRET"] = getKeyValue("chainlit-secret")
# os.environ["CHAINLIT_ROOT_PATH"] = "/"

# database.establishDbConnection()
 

async def updateIPBasedMsgCount():
    requests.post("http://localhost:8086/requestcount/ip")

async def updateEmailBasedMsgCount():
    email = cl.user_session.get("email")
    requests.post("http://localhost:8086/requestcount/email/" + email)


# from database import *
from Project import *
from search import *
from news import *
from research import *
from image import *
from video import *

@cl.on_message
async def on_message(message: cl.Message):
    
    currentReqCount = cl.user_session.get("curReqCount")
    maxReqCount = cl.user_session.get("maxReqCount")

    requestsnotfound = False
    if(currentReqCount == None or maxReqCount == None):
        currentReqCount = 0
        maxReqCount = 1000
        requestsnotfound = True

    if(  currentReqCount > maxReqCount):
        content = {"command":"limitreached","status":"processing"}
        await cl.send_window_message(content)
        return

    prompt = message.content
    # mode = cl.user_session.get("mode")
    command = message.command 
    if command == None:
        command = "Search"
    
    showSpinner = True
    progreselem = cl.CustomElement(name="SimpleSearchProgress", display="inline")
    progressmsg = cl.Message(content="", elements=[progreselem], author="Infinity")
    await asyncio.gather(updateProgress(progressmsg, "Thinking...", showSpinner, False))
 
    if command == "Search":
        await conductSearch(prompt,progressmsg,agents_client,agent,thread,thread2)
        await asyncio.gather(updateProgress(progressmsg, "", False, False))
    
    elif command == "Project":
        await conductProject(prompt,progressmsg)
        await asyncio.gather(updateProgress(progressmsg, "", False, False))
    
    elif command == "World News":
        await PerformNews(message.content)
        await asyncio.gather(updateProgress(progressmsg, "", False, False))
        return
    
    elif command == "Research":
        await performResearch(message.content)
        await asyncio.gather(updateProgress(progressmsg, "", False, False))
        return

    elif command == "Image":
        await performImage(message.content)
        await asyncio.gather(updateProgress(progressmsg, "", False, False))
        return
    
    elif command == "Video":
        bytes = await performVideo(message.content)
        # mp4bytes = await convertBytesToMP4(bytes)
        video = cl.Video(contnet=bytes)
        await cl.Message(content="",elements=[video]).send()
        await asyncio.gather(updateProgress(progressmsg, "", False, False))
 
        return

    email = cl.user_session.get("email")

    # try:
    #     if email == None:
    #         await updateIPBasedMsgCount()
    #     else:
    #         await updateEmailBasedMsgCount()

    #     if requestsnotfound:
    #         content = {"command": "getreqlimits", "status": "processing"}
    #         await cl.send_window_message(content)

    # except Exception as ex:
    #     print(str(ex))

    cl.user_session.set("curReqCount", currentReqCount + 1)
    await asyncio.gather(updateProgress(progressmsg, "Done", False, True))


