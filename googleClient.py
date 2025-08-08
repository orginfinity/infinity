
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
secrets["sqlloginpwd"] = None
secrets["google-auth-secret"] = None
secrets["google-client-id"] = None
secrets["chainlit-secret"] = None
secrets["azure-openai-key"] = None


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

def getWebsitesProps(websites,titles,favicons, contents,thumbnails,start):
    # logger.info("Contents: %s", websites)
    """Pretending to fetch data from linear"""
    websitesProps = {}

    i = 0
    sourceCount = 0
    # for i in range(len(websites)):

    try:
        while i < len(websites):
            if(i < len(websites) and i < len(titles) and i < len(favicons) and i < len(contents) and i < len(thumbnails)):
                websiteKey = "website"+str(start) 

                contentsKey = "contents"+str(start)
                thumbnailKey = "thumbnail"+str(start)
                titlesKey = "titles"+str(start)
                faviconKey = "favicon"+str(start)
                
                if websites[i] != None and contents[i] !=  None and thumbnails[i] != None and titles[i] != None and favicons[i] != None:
                    # logger.info("WEBSITE : %s\n",websites[i])
                    websitesProps[websiteKey] = websites[i]
                    websitesProps[contentsKey] = contents[i]
                    websitesProps[thumbnailKey] = thumbnails[i]
                    websitesProps[titlesKey] = titles[i]
                    websitesProps[faviconKey] = favicons[i]
                    sourceCount += 1
                    start += 1
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

def getImagesProps(images):
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

def get_images_fromgoogle(prompt):

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
        props =  getImagesProps(images)
 
    return props 

def get_websites_fromgoogle(prompt,start):
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
        print(e)
    finally:
        props =  getWebsitesProps(websites,titles, favicons, contents,thumbnails,start)
        props["prompt"] = prompt
    
    return props 