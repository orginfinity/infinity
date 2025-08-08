import uuid

import chainlit as cl
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Import packages
import os
import sys
from openai import AsyncAzureOpenAI, AzureOpenAI
import logging
from azure.identity import DefaultAzureCredential
# from azure.identity import  get_bearer_token_provider, DefaultAzureCredentialOptions
from dotenv import load_dotenv
from dotenv import dotenv_values
from chainlit.input_widget import Select, Switch, Slider
import json
import requests

import database
from googleClient import *
secrets = {}
secrets["google-search-uri"] = None
secrets["google-fav-icons-uri"] = None
secrets["agent-uri"] = None
secrets["google-auth-secret"] = None
secrets["google-client-id"] = None
secrets["chainlit-secret"] = None
secrets["azure-openai-key"] = None

# def getKeyValue(secret_name):
#
#     if secret_name not in secrets.keys():
#         return None
#
#     if secrets[secret_name] != None:
#         return secrets[secret_name]
#
#     key_vault_url = "https://infinity.vault.azure.net/"
#     credential = DefaultAzureCredential()
#     client = SecretClient(vault_url=key_vault_url, credential=credential)
#
#     try:
#         # Retrieve the secret
#         retrieved_secret = client.get_secret(secret_name)
#         secrets[secret_name] = retrieved_secret.value
#         return retrieved_secret.value
#     except Exception as e:
#         print(e)
#         return None
    
google_search_uri = getKeyValue("google-search-uri")
google_fav_icons_uri = getKeyValue("google-fav-icons-uri") 
agent_uri =  getKeyValue("agent-uri")  

temperature = 0.9  
# api_key = getKeyValue("api-key")
api_type = "azure"
api_version = "2024-12-01-preview"
engine = "gpt-4o"
model ="gpt-4o"

system_content = "Do not ask any clarifying questions."
max_retries = 5
timeout = 30
debug = "true"  
 
import os
from typing import Any
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    MessageDeltaChunk,   
    MessageRole,
    MessageDeltaTextUrlCitationAnnotation,
    MessageDeltaTextContent, 
)
  
async def getWebsitesProps(websites,titles,favicons, contents,thumbnails):
    # logger.info("Contents: %s", websites)
    """Pretending to fetch data from linear"""
    websitesProps = {}

    i = 0
    sourceCount = 0
    # for i in range(len(websites)):

    try:
        while i < len(websites):
            if(i < len(websites) and i < len(titles) and i < len(favicons) and i < len(contents) and i < len(thumbnails)):
                websiteKey = "website"+str(i) 

                contentsKey = "contents"+str(i)
                thumbnailKey = "thumbnail"+str(i)
                titlesKey = "titles"+str(i)
                faviconKey = "favicon"+str(i)
                
                if websites[i] != None and contents[i] !=  None and thumbnails[i] != None and titles[i] != None and favicons[i] != None:
                    # logger.info("WEBSITE : %s\n",websites[i])
                    websitesProps[websiteKey] = websites[i]
                    websitesProps[contentsKey] = contents[i]
                    websitesProps[thumbnailKey] = thumbnails[i]
                    websitesProps[titlesKey] = titles[i]
                    websitesProps[faviconKey] = favicons[i]
                    sourceCount += 1
            i += 1
    except Exception as e:
        print("Error while preparing websites props \n %s",e)
    finally: 
        websitesProps["sourceCount"] = sourceCount
        
    return websitesProps

class imageFromGoogle:
    def __init__(self,link,displayLink,contextLink):
        self.link =link
        self.displayLink = displayLink
        self.contextLink = contextLink

def get_fav_icons(websites):
    # logger.info("to get icons: %s",websites)
    icons = []
    for website in websites:
        uri = google_fav_icons_uri + website + "&size=32"
         
        icons.append(uri)
    return icons

async def getImagesProps(images):
    imagesProps = {}

    i = 0
    imageCount = 0

    try:
        while i < len(images):
            thumbnailLinkKey = "thumbnailLink" + str(i)
            thumbnailLink = images[i].link
            imagesProps[thumbnailLinkKey] = thumbnailLink

            
            displayLinkKey = "displayLink" + str(i)
            displayLink = images[i].displayLink
            imagesProps[displayLinkKey] = displayLink
    
            contextLinkkey = "contextLink" + str(i)
            contextLink = images[i].contextLink
            imagesProps[contextLinkkey] = contextLink

            if thumbnailLink != None and displayLink != None and contextLink != None:
                imagesProps[thumbnailLinkKey] = thumbnailLink
                imagesProps[displayLinkKey] = displayLink
                imagesProps[contextLinkkey] = contextLink
                imageCount += 1
            i += 1
    except Exception as e:
        print("Error while populating image props from Google\n%s",e)
    finally:
        imagesProps["imagesCount"] = imageCount
  
    return imagesProps

async def get_images_fromgoogle(prompt):

    try:
        uri = google_search_uri + prompt +"&searchType=image" + "&imgSize=medium" 
        data = requests.get(uri).json()
        search_items = data.get("items") 
        images = [] 
        
        for i, search_item in enumerate(search_items, start=1):
            content = ""
            imgObject = search_item.get("image")
            image = imageFromGoogle(search_item.get("link"), search_item.get("displayLink"),imgObject.get("contextLink"))

            if(image.link != None and image.contextLink != None and image.displayLink != None):
                images.append(image)
    except:
        print("Error while getting images from google:\n %s",len(images))
    finally:
        props =  await getImagesProps(images)
 
    return props 

async def get_websites_fromgoogle(prompt):
    try:
        uri = google_search_uri + prompt
    
        data = requests.get(uri).json()
        search_items = data.get("items")

    # iterate over 10 results found
        contents = []
        websites = []
        thumbnails = []
        titles = []
        favicons = []
        
        if(search_items == None):
            return
    
        for i, search_item in enumerate(search_items, start=1):
            content = ""
    
            link = search_item.get("link")
            websites.append(link)
            
            # get the page title        
            title = search_item.get("title")
            titles.append(title)
            # page snippet
            snippet = search_item.get("snippet")
        
            content += snippet + "\n"
            
            pagemap = search_item.get("pagemap")

            if pagemap != None:

                cse_thumbnail = pagemap.get("cse_thumbnail")
                if cse_thumbnail != None :
                    if len(cse_thumbnail) > 0:
                        cse_thumbnail = cse_thumbnail[0]      
                        src = cse_thumbnail.get("src")
                        if src != None:
                            thumbnails.append(src)

            contents.append(content) 
        favicons = get_fav_icons(websites)
        
    except Exception as e:
        print("Error while fetching websites from google \n%s",e)
    finally:
        props =  await getWebsitesProps(websites,titles, favicons, contents,thumbnails)       
        props["prompt"] = prompt
    
    return props 

async def get_questionsProps(questions):
    props = {}
    try:
        if questions["Q1"] != None:
            props["question1"] =questions["Q1"]
        if questions["Q2"] != None:
            props["question2"] =questions["Q2"]
        if questions["Q3"] != None:
            props["question3"] =questions["Q3"]
        if questions["Q4"] != None:
            props["question4"] =questions["Q4"]
 
    except Exception as e:
        print("Exception while preparing questions props:\n%s",e)
    finally:
        return props 
 
# @cl.action_callback("followup_questions_action")
# async def on_action(action):
#     payload = action.payload
#     val = payload["value"]
#     sources_element = cl.CustomElement(name="LinearTicket",props=val)
#     await cl.Message(content="",elements=[sources_element]).update()

from collections import defaultdict
messages = defaultdict(int)
project_client = None
agents_client= None
agent = None 

@cl.on_chat_start
async def on_chat_start():

    content = {"command":"useremail","status":"processing"}
    await cl.send_window_message(content)

    content = {"command":"getreqlimits","status":"processing"}
    await cl.send_window_message(content)

    cl.user_session.set("mode","search")
    settings = await cl.ChatSettings(
        [
            Select(
                id="Mode",
                label="Mode",
                values=["Audio", "Books", "Research", "Regular"],
                initial_index=3,
            ),
            ]).send()
    monitor_element = cl.CustomElement(name="Monitor")
    await cl.Message(content="",elements=[monitor_element]).send()

    await setup_openai_realtime()

    message_history = [{"role": "system", "content": system_content}] 
    cl.user_session.set("message_history",  message_history )

    try:
        project_client = cl.user_session.get("project_client")
        if project_client == None:
            project_client = AIProjectClient(endpoint= agent_uri,credential=DefaultAzureCredential())
            cl.user_session.set("project_client", project_client) 
            
    except Exception as e: 
        print("Error while creating project_client: \n%s",e)
        return

    try:
        agents_client = cl.user_session.get("agents_client")
        if agents_client == None:
            agents_client = project_client.agents             
            cl.user_session.set("agents_client", agents_client) 
            
    except Exception as e: 
        print("Error while creating agents_client: \n%s",e)
        return 
 
    try:
        agent = cl.user_session.get("agent")
        if agent == None:
            agent = agents_client.get_agent("asst_58piOsPpG4mOb2CdVWZC9uPF")
            cl.user_session.set("agent", agent) 
            
    except Exception as e:
        print("Error while creating agent: \n%s",e)
        return  
    
    try:
        thread = cl.user_session.get("thread")
        if thread == None:
            thread = agents_client.threads.create()
            cl.user_session.set("thread", thread)

        thread2 = cl.user_session.get("thread2")
        if thread2 == None:
            thread2 = agents_client.threads.create()
            cl.user_session.set("thread2", thread2)
            
    except Exception as e:
        print("Error while creating agent: \n%s",e)
        return  

    try:
        print('hello')
        # logger = cl.user_session.get("logger")
        # if logger == None:
        #     logger = logging.getLogger(__name__)
        #     cl.user_session.set("logger", logger)
            
    except Exception as e:
        print("Error while logger: \n%s",e)
        return

    content =  "started"
    await cl.send_window_message(content)

 # from database import establishDbConnection
# establishDbConnection()

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

async def returnError():
    image = cl.Image(path="./maintenance.gif", name="image1", display="inline") 
    await cl.Message(
            content="There was an error establishing session. We are on it!",
            # elements=[image],
        ).send()

async def sendResponseMessage(prompt):
    try:
        global logger
        # logger = cl.user_session.get("logger")
        sources_element_props = await get_websites_fromgoogle(prompt)
        images_element_props = await get_images_fromgoogle(prompt)

        if sources_element_props["sourceCount"] != 0 or images_element_props["imagesCount"] != 0:
            headerProps = sources_element_props | images_element_props
            headerProps["prompt"] = prompt

            Header  = cl.CustomElement(name="Header",props=headerProps, display="inline")   
            headerMsg = cl.Message(content="",elements=[Header],  author="Infinity")
            await headerMsg.send()

        response, result = await StreamAgentResponse(prompt)
  
        return result
    except Exception as e:
        await returnError()

        print("Error while streaming message\n%s",e)
        return False
    
async def StreamAgentResponse(prompt, forUris= False ):

    try:
        agents_client = cl.user_session.get("agents_client")
        agent = cl.user_session.get("agent")
        logger = cl.user_session.get("logger")

        if not forUris:
            thread = cl.user_session.get("thread") 
        else:
            thread = cl.user_session.get("thread2")

        message = agents_client.messages.create(thread_id=thread.id,role=MessageRole.USER,content=prompt)
        result = ""
        answerMsg = cl.Message(content="",  author="Infinity") 
        with agents_client.runs.stream(thread_id=thread.id, agent_id=agent.id) as stream:         
            for event_type, event_data, _ in stream:
                if isinstance(event_data, MessageDeltaChunk): 
                    if not forUris:       
                        await answerMsg.stream_token(event_data.text)    
                        if event_data.delta.content and isinstance(event_data.delta.content[0], MessageDeltaTextContent):
                            delta_text_content = event_data.delta.content[0]
                            if delta_text_content.text and delta_text_content.text.annotations:
                                for delta_annotation in delta_text_content.text.annotations:
                                    if isinstance(delta_annotation, MessageDeltaTextUrlCitationAnnotation):                                                 
                                        await answerMsg.stream_token(f"\nCitation: [{delta_annotation.url_citation.title}]({delta_annotation.url_citation.url})")
                    
            response_message = agents_client.messages.get_last_message_by_role(thread_id=thread.id, role=MessageRole.AGENT)
            
            if response_message:
                for text_message in response_message.text_messages:
                    result += text_message.text.value
        
            return result,True
    except Exception as e:
        return False 
    
async def sendFollowupQuestions(prompt):
    prompt = "give me response in the following JSON format {\"Q1\":\"..\",\"Q2\":\"..\",\"Q3\":\"..\",\"Q4\":\"..\"}. " \
             "Q1,Q2,Q3 and Q4 are for the follow up questions to the prompt. Your prompt is this -" + prompt
    questions = await StreamAgentResponse(prompt, True)

    try:
        questions = json.loads(questions[0])
        questions_element_props = await get_questions(questions)
        questions_element = cl.CustomElement(name="FollowUpQuestions", props=questions_element_props)
        msg = cl.Message(content="", elements=[questions_element], author="Infinity")
        await msg.send()
    except Exception as e:
        print(e)


os.environ["OAUTH_GOOGLE_CLIENT_ID"] = getKeyValue("google-client-id")
os.environ["OAUTH_GOOGLE_CLIENT_SECRET"] = getKeyValue("google-auth-secret")
os.environ["CHAINLIT_AUTH_SECRET"] = getKeyValue("chainlit-secret")
os.environ["CHAINLIT_ROOT_PATH"] = "/"

print(str(os.environ["OAUTH_GOOGLE_CLIENT_ID"]))
print(str(os.environ["OAUTH_GOOGLE_CLIENT_SECRET"]))

database.establishDbConnection()

@cl.action_callback("action_button")
async def on_action(action):
    try:
        correlationId = cl.user_session.get("correlationId")

        clientSummaries = get_matching_question_action(correlationId)
        # clientSummaries = requests.get("http://localhost:8086//summaries/"+correlationId)
        count = 0
        propsVar = {}
        for summary in clientSummaries:

            promptVar = "prompt" + str(count)
            actionVar = "action" + str(count)
            sourcesVar = "sources" + str(count)
            faviconVar = "favicon" + str(count)

            propsVar[promptVar] = summary[0]
            propsVar[actionVar] = summary[1]
            sources = summary[3].replace("'", "\"")
            propsVar[sourcesVar] = json.loads(sources)

            favicons = summary[4].replace("'", "\"")
            propsVar[faviconVar] = json.loads(favicons)


            count += 1

        if count > 0:
            propsVar["promptactioncount"] = count
            ResearchSteps = cl.CustomElement(name="ResearchSteps", props=propsVar, display="inline")
            ResearchStepsMsg = cl.Message(content="", elements=[ResearchSteps], author="Infinity")
            await ResearchStepsMsg.send()

            ResearchStepsMsg = cl.Message(content="", author="Infinity")
            await ResearchStepsMsg.send()
            update_stagemetadata(1, correlationId)

    except Exception as ex:
        print(ex)

async def get_questions(questions):
    """Pretending to fetch data from linear"""
    return {
        "question1":questions["Q1"],
        "question2":questions["Q2"],
        "question3":questions["Q3"],
        "question4":questions["Q4"]
    }

def updateIPBasedMsgCount():
    requests.post("http://localhost:8086/requestcount/ip")

def updateEmailBasedMsgCount():
    email = cl.user_session.get("email")
    requests.post("http://localhost:8086/requestcount/email/" + email)

from database import *
from fastapi import Request
@cl.on_message
async def on_message(message: cl.Message):

    currentReqCount = cl.user_session.get("curReqCount")
    maxReqCount = cl.user_session.get("maxReqCount")

    if(currentReqCount == None or maxReqCount == None):
        content = {"command": "getreqlimits", "status": "processing"}
        await cl.send_window_message(content)
        await cl.Message(content="There was an error. Please try again later.").send()

    if(currentReqCount > maxReqCount):
        content = {"command":"limitreached","status":"processing"}
        await cl.send_window_message(content)
        return

    prompt = message.content
    mode = cl.user_session.get("mode")

    if mode == "search":
        # if checkForSessionVariables() == False:
        #     await returnError()
        #     return
        try:
            result = await sendResponseMessage(prompt)
            if result:
                await sendFollowupQuestions(prompt)

        except Exception as e:
            print("Error in OnMessage:\n%s",e)
    else:
        correlationId = str(uuid.uuid4())
        try:
            cl.user_session.set("correlationId", correlationId)
            create_prompt(message.content,0,uuid.uuid4())

            prompt = {
                "prompt": message.content,
                "correlationId": correlationId
            }

            requests.post("http://localhost:8088/prompt",json=prompt)
            propsVar = {"correlationId": correlationId}
            ResearchTopHeader = cl.CustomElement(name="Research", props=propsVar, display="inline")
            researchTopHeaderMsg = cl.Message(content="", elements=[ResearchTopHeader],author="Infinity")
            await researchTopHeaderMsg.send()

        except Exception as ex:
            print(ex)

    email = cl.user_session.get("email")
    if email == None:
        updateIPBasedMsgCount()
    else:
        updateEmailBasedMsgCount()
    cl.user_session.set("curReqCount", currentReqCount + 1)

@cl.on_window_message
async def window_message(message: str):
    first_key = next(iter(message))
    cl.user_session.set(first_key, message[first_key])

from realtime import RealtimeClient
from realtime.tools import tools
import asyncio
from openai import AsyncOpenAI

async def setup_openai_realtime():
    """Instantiate and configure the OpenAI Realtime Client"""
    openai_realtime = RealtimeClient(api_key=getKeyValue("azure-openai-key"))
    cl.user_session.set("track_id", str(uuid.uuid4()))

    async def handle_conversation_updated(event):
        item = event.get("item")
        delta = event.get("delta")
        """Currently used to stream audio back to the client."""
        if delta:
            # Only one of the following will be populated for any given event
            if "audio" in delta:
                audio = delta["audio"]  # Int16Array, audio added
                await cl.context.emitter.send_audio_chunk(
                    cl.OutputAudioChunk(
                        mimeType="pcm16",
                        data=audio,
                        track=cl.user_session.get("track_id"),
                    )
                )
            if "transcript" in delta:
                transcript = delta["transcript"]  # string, transcript added
                pass
            if "arguments" in delta:
                arguments = delta["arguments"]  # string, function arguments added
                pass

    async def handle_item_completed(item):
        """Used to populate the chat context with transcription once an item is completed."""
        # print(item) # TODO
        pass

    async def handle_conversation_interrupt(event):
        """Used to cancel the client previous audio playback."""
        cl.user_session.set("track_id", str(uuid.uuid4()))
        await cl.context.emitter.send_audio_interrupt()

    async def handle_error(event):
        print(event)

    openai_realtime.on("conversation.updated", handle_conversation_updated)
    openai_realtime.on("conversation.item.completed", handle_item_completed)
    openai_realtime.on("conversation.interrupted", handle_conversation_interrupt)
    openai_realtime.on("error", handle_error)

    cl.user_session.set("openai_realtime", openai_realtime)
    coros = [
        openai_realtime.add_tool(tool_def, tool_handler)
        for tool_def, tool_handler in tools
    ]
    await asyncio.gather(*coros)

@cl.on_audio_start
async def on_audio_start():
    try:
        msg = {"command": "useremail"}
        await cl.send_window_message(msg)

        isValid = await validate()
        if not isValid:
            return

        openai_realtime: RealtimeClient = cl.user_session.get("openai_realtime")
        if openai_realtime == None:
            await cl.Message(content="Still setting up audio connectors. Please try again").send()
            return

        useremail = cl.user_session.get("useremail")
        if useremail == None or  useremail == "" or useremail == "default":
            content = "userpanel:Please login to exprience audio chat."
            await cl.send_window_message(content)
            return


        await openai_realtime.connect()
        # logger.info("Connected to OpenAI realtime")
        # TODO: might want to recreate items to restore context
        # openai_realtime.create_conversation_item(item)
        return True
    except Exception as e:
        await cl.ErrorMessage(
            content=f"Failed to connect to OpenAI realtime: {e}"
        ).send()
        return False

@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.InputAudioChunk):

    openai_realtime: RealtimeClient = cl.user_session.get("openai_realtime")
    if openai_realtime.is_connected():
        await openai_realtime.append_input_audio(chunk.data)
    else:
        print("RealtimeClient is not connected")

@cl.on_audio_end
@cl.on_chat_end
@cl.on_stop
async def on_end():
    openai_realtime: RealtimeClient = cl.user_session.get("openai_realtime")
    if openai_realtime and openai_realtime.is_connected():
        await openai_realtime.disconnect()

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://proud-hill-0b342cf00.1.azurestaticapps.net", "http://localhost:3000",
                   "https://localhost:8082/auth/login","http://localhost:8088"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
