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
# from bs4 import BeautifulSoup  


def getKeyValue(secret_name):
    key_vault_url = "https://infinity.vault.azure.net/"

    # Authenticate using DefaultAzureCredential
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_url, credential=credential)
 
    try:
        # Retrieve the secret
        retrieved_secret = client.get_secret(secret_name)
        return retrieved_secret.value
    except Exception as e:
        print(e)
        return None

temperature = 0.9  
# api_key = getKeyValue("api-key")
api_type = "azure"
api_version = "2024-12-01-preview"
engine = "gpt-4o"
model ="gpt-4o"

system_content = "You are a helpful assistant."
max_retries = 5
timeout = 30
debug = "true" 
google_search_uri = getKeyValue("google-search-uri")
google_fav_icons_uri = getKeyValue("google-fav-icons-uri") 
agent_uri =  getKeyValue("agent-uri")  
 
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
 

@cl.on_chat_start
async def on_chat_start():  
    message_history = [{"role": "system", "content": system_content}] 
    cl.user_session.set("message_history",  message_history )

logger = logging.getLogger(__name__)

async def getWebsitesProps(websites,titles,favicons, contents,thumbnails):
    # logger.info("Contents: %s", websites)
    """Pretending to fetch data from linear"""
    websitesProps = {}

    i = 0
    sourceCount = 0
    # for i in range(len(websites)):
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
    # logger.info("website props%s",websitesProps)
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

    imagesProps["imagesCount"] = imageCount
    # logger.info("\nIMAGES\n: %s",imagesProps)
    return imagesProps

async def get_images_fromgoogle(prompt):
    uri = google_search_uri + prompt +"&searchType=image" + "$imgSize=medium"
 
    data = requests.get(uri).json()
    search_items = data.get("items")

# iterate over 10 results found
    images = [] 
     
    for i, search_item in enumerate(search_items, start=1):
        content = ""
        imgObject = search_item.get("image")
        image = imageFromGoogle(search_item.get("link"), search_item.get("displayLink"),imgObject.get("contextLink"))

        if(image.link != None and image.contextLink != None and image.displayLink != None):
            images.append(image)
    logger.info("LENGTH: %s",len(images))
    props =  await getImagesProps(images)
 
    return props 

async def get_websites_fromgoogle(prompt):
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
    try:

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
        props =  await getWebsitesProps(websites,titles, favicons, contents,thumbnails)
       
        props["prompt"] = prompt
        return props 
    except:
        return None

async def get_questions(questions):
    """Pretending to fetch data from linear"""
    return {
        "question1":questions["Q1"],
        "question2":questions["Q2"],
        "question3":questions["Q3"],
        "question4":questions["Q4"] 
    }
 
@cl.action_callback("followup_questions_action")
async def on_action(action):
    payload = action.payload
    val = payload["value"]
    sources_element = cl.CustomElement(name="LinearTicket",props=val) 
    await cl.Message(content="",elements=[sources_element]).update()

project_client = AIProjectClient(
            endpoint= agent_uri,
            credential=DefaultAzureCredential(),
        )

agents_client = project_client.agents
agent = agents_client.get_agent("asst_58piOsPpG4mOb2CdVWZC9uPF")
thread = agents_client.threads.create()


@cl.on_message
async def on_message(message: cl.Message):  
    try:    
        sources_element_props = await get_websites_fromgoogle(message.content)   
        images_element_props = await get_images_fromgoogle(message.content)
        props = sources_element_props | images_element_props
        Header  = cl.CustomElement(name="Header",props=props, display="inline")   
        headerMsg = cl.Message(content="",elements=[Header],  author="Infinity")
        await headerMsg.send()
    
        answerMsg = cl.Message(content="",  author="Infinity") 
        async def StreamAgentResponse(prompt, forUris= False ):
            
            message = agents_client.messages.create(
                        thread_id=thread.id,
                        role=MessageRole.USER,
                        content=prompt,
                    )
            result = ""
            
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
        
            return result
        
        await StreamAgentResponse(message.content)
    
    
        prompt = "give me response in the following JSON format {\"Q1\":\"..\",\"Q2\":\"..\",\"Q3\":\"..\",\"Q4\":\"..\"}. " \
        "Q1,Q2,Q3 and Q4 are for the follow up questions to the prompt. Your prompt is this -" + message.content

        questions = await StreamAgentResponse(prompt,True)        
    
        questions = json.loads(questions)
        questions_element_props = await get_questions(questions) 
        questions_element = cl.CustomElement(name="FollowUpQuestions",props=questions_element_props )
        msg = cl.Message(content="",elements=[questions_element], author="Infinity")   
        await msg.send()
    except Exception as e :
        print(e)

    # prompt = "give me response in the following JSON format {\"Uris\":\"..\" }. " \
    # "In Uris field, give me an array of 10 URLs related to the prompt. Your prompt is this - " + message.content

    # Uris = await StreamAgentResponse(prompt,True)
    
    # websites = json.loads(Uris)
    # websites_element_props = await getWebsitesProps(websites) 
    # websites_element = cl.CustomElement(name="Websites",props=websites_element_props )
    # msg = cl.Message(content="",elements=[websites_element], author="Infinity")   
    # await msg.send()

    # message_history = cl.user_session.get("message_history") 
    # message_history.append({"role": "user", "content": message.content+ " . Response should be in markdown format."})
    
 
    # answerMsg = cl.Message(content="",  author="Infinity") 
    # answer = ""
       

# @cl.on_message
# async def main(message: cl.Message):
#     # Your custom logic goes here...

#     # Send a response back to the user
#     await cl.Message(
#         content=getKeyValue("test"),
#     ).send()

#from flask import Flask

#app = Flask(__name__)

#@app.route('/')
#def hello_world():
    #return '<html>Hello World!</html>'

#if __name__ == '__main__':
 #   app.run()