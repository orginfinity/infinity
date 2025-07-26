import uuid

import chainlit as cl
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient 
import chainlit as cl
# Import packages
import os
import sys
from openai import AsyncAzureOpenAI, AzureOpenAI
import logging
import chainlit as cl
from azure.identity import DefaultAzureCredential    
# from azure.identity import  get_bearer_token_provider, DefaultAzureCredentialOptions
from dotenv import load_dotenv
from dotenv import dotenv_values
from chainlit.input_widget import Select, Switch, Slider
import json
import requests 


secrets = {}
secrets["google-search-uri"] = None
secrets["google-fav-icons-uri"] = None
secrets["agent-uri"] = None
secrets["google-auth-secret"] = None
secrets["google-client-id"] = None
secrets["chainlit-secret"] = None

def getKeyValue(secret_name):

    if secret_name not in secrets.keys():
        return None
    
    if secrets[secret_name] != None:
        return secrets[secret_name]
    
    key_vault_url = "https://infinity.vault.azure.net/" 
    credential = DefaultAzureCredential() 
    client = SecretClient(vault_url=key_vault_url, credential=credential)
    
    try:
        # Retrieve the secret
        retrieved_secret = client.get_secret(secret_name)
        secrets[secret_name] = retrieved_secret.value
        return retrieved_secret.value
    except Exception as e:
        print(e)
        return None 
    
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
        logger = cl.user_session.get("logger")
        logger.error("Error while preparing websites props \n %s",e)
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
        logger = cl.user_session.get("logger")
        logger.info("Error while populating image props from Google\n%s",e)
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
        logger = cl.user_session.get("logger")
        logger.info("Error while getting images from google:\n %s",len(images))
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
        logger = cl.user_session.get("logger")
        logger.info("Error while fetching websites from google \n%s",e)
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
        logger = cl.user_session.get("logger")
        logger.info("Exception while preparing questions props:\n%s",e)
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
    message_history = [{"role": "system", "content": system_content}] 
    cl.user_session.set("message_history",  message_history )

    try:
        project_client = cl.user_session.get("project_client")
        if project_client == None:
            project_client = AIProjectClient(endpoint= agent_uri,credential=DefaultAzureCredential())
            cl.user_session.set("project_client", project_client) 
            
    except Exception as e: 
        logger.error("Error while creating project_client: \n%s",e)
        return

    try:
        agents_client = cl.user_session.get("agents_client")
        if agents_client == None:
            agents_client = project_client.agents             
            cl.user_session.set("agents_client", agents_client) 
            
    except Exception as e: 
        logger.error("Error while creating agents_client: \n%s",e)
        return 
 
    try:
        agent = cl.user_session.get("agent")
        if agent == None:
            agent = agents_client.get_agent("asst_58piOsPpG4mOb2CdVWZC9uPF")
            cl.user_session.set("agent", agent) 
            
    except Exception as e: 
        logger.error("Error while creating agent: \n%s",e) 
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
        logger.error("Error while creating agent: \n%s",e) 
        return  

    try:
        logger = cl.user_session.get("logger")
        if logger == None:
            logger = logging.getLogger(__name__)
            cl.user_session.set("logger", logger)
            
    except Exception as e: 
        logger.error("Error while logger: \n%s",e) 
        return

# from database import establishDbConnection
# establishDbConnection()

def checkForSessionVariables():
 
    try:
        project_client = cl.user_session.get("project_client")
        agents_client = cl.user_session.get("agents_client")
        agent = cl.user_session.get("agent")
        logger = cl.user_session.get("logger")
        thread = cl.user_session.get("thread")
        thread2 = cl.user_session.get("thread2")
    except Exception as e:
        return False

    if project_client == None or agents_client == None or agent == None or  thread == None or logger == None or thread2 == None:
            return False
    
    return True

async def returnError():
    image = cl.Image(path="./maintenance.gif", name="image1", display="inline") 
    await cl.Message(
            content="There was an error establishing session. We are on it!",
            # elements=[image],
        ).send()

async def sendResponseMessage(message: cl.Message):
    try:
        logger = cl.user_session.get("logger") 
        sources_element_props = await get_websites_fromgoogle(message.content)   
        images_element_props = await get_images_fromgoogle(message.content)

        if sources_element_props["sourceCount"] != 0 or images_element_props["imagesCount"] != 0:
            headerProps = sources_element_props | images_element_props
            headerProps["prompt"] = message.content

            Header  = cl.CustomElement(name="Header",props=headerProps, display="inline")   
            headerMsg = cl.Message(content="",elements=[Header],  author="Infinity")
            await headerMsg.send()

        response, result = await StreamAgentResponse(message.content)
  
        return result
    except Exception as e:
        await returnError()
        logger.error("Error while streaming message\n%s",e)
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
    
def sendFollowupQuestions(prompt):
    try:
        prompt = "give me response in the following JSON format {\"Q1\":\"..\",\"Q2\":\"..\",\"Q3\":\"..\",\"Q4\":\"..\"}. " \
                 "Q1,Q2,Q3 and Q4 are for the additional prompts you may want to suggest the user based on the prompt. Do not respond with questions but statements." \
                 " Do not ask any clarifying questions. Do not ask any personal questions about the user." \
                 "     Your prompt is this - " + prompt

        from openai import OpenAI
        client = OpenAI()
        client.api_key = getKeyValue("azure-openai-key")
        response = client.responses.create(
            model="gpt-4.1",
            input=prompt
        )
        return response.output_text
        # print(response.output_text)

    except Exception as e:
        print("Error while building follow up questions!\n%s", e)

os.environ["OAUTH_GOOGLE_CLIENT_ID"] = getKeyValue("google-client-id")
os.environ["OAUTH_GOOGLE_CLIENT_SECRET"] = getKeyValue("google-auth-secret")
os.environ["CHAINLIT_AUTH_SECRET"] = getKeyValue("chainlit-secret")

from typing import Dict, Optional
@cl.oauth_callback
def oauth_callback(
  provider_id: str,
  token: str,
  raw_user_data: Dict[str, str],
  default_user: cl.User,
) -> Optional[cl.User]:
  return default_user


# @cl.header_auth_callback
# def header_auth_callback(headers: Dict) -> Optional[cl.User]:
#   # Verify the signature of a token in the header (ex: jwt token)
#   # or check that the value is matching a row from your database
#   name = headers.get("name")
#   email = headers.get("email")
#   print(name)
#   if name != None:
#     cl.user_session.set("name", name)
#     cl.user_session.set("email", email)
#     return cl.User(identifier=name, metadata={"role": "user", "provider": "header"})
#   else:
#     return None

@cl.action_callback("action_button")
async def on_action(action):
    try:
        correlationId = cl.user_session.get("correlationId")
        clientSummaries = get_matching_question_action(correlationId)

        count = 0
        propsVar = {}
        for summary in clientSummaries:

            promptVar = "prompt" + str(count)
            actionVar = "action" + str(count)
            sourcesVar = "sources" + str(count)
            faviconVar = "favicon" + str(count)

            propsVar[promptVar] = summary[0]
            propsVar[actionVar] = summary[1]
            propsVar[sourcesVar] = summary[3]
            propsVar[faviconVar] = summary[4]

            update_stage(1, summary[0], correlationId)
            count += 1

        if count > 0:
            propsVar["promptactioncount"] = count
            ResearchSteps = cl.CustomElement(name="ResearchSteps", props=propsVar, display="inline")
            ResearchStepsMsg = cl.Message(content="", elements=[ResearchSteps], author="Infinity")
            await ResearchStepsMsg.send()

            ResearchStepsMsg = cl.Message(content="", author="Infinity")
            await ResearchStepsMsg.send()

    except Exception as ex:
        print(ex)

# from database import  *
from serviceBus import *
@cl.on_message
async def on_message(message: cl.Message):
    name = cl.user_session.get("name")
    print(name)
    headerMsg = cl.Message(content=name, author="Infinity")
    await headerMsg.send()
    return
    # correlationId = str(uuid.uuid4())
    # try:
    #     cl.user_session.set("correlationId", correlationId)
    #     create_prompt(message.content,0,uuid.uuid4())
    #
    #     prompt = {
    #         "prompt": message.content,
    #         "correlationId": correlationId
    #     }
    #
    #     publish_message_to_topic(json.dumps(prompt))
    #     propsVar = {"correlationId": correlationId}
    #     ResearchTopHeader = cl.CustomElement(name="ResearchTopHeader", props=propsVar, display="inline")
    #     researchTopHeaderMsg = cl.Message(content="", elements=[ResearchTopHeader],author="Infinity")
    #     await researchTopHeaderMsg.send()
    #
    # except Exception as ex:
    #     print(ex)
    #
    # logger = cl.user_session.get("logger")
   #
   #
    if checkForSessionVariables() == False:
        await returnError()
        return
    try:

        result = await sendResponseMessage(message)

        if result:
            await sendFollowupQuestions(message)

    except Exception as e:
        logger.error("Error in OnMessage:\n%s",e)
