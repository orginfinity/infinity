from openai import OpenAI
from common import getKeyValue
import chainlit as cl
from common import *
async def performImage(progressmsg,prompt):
    
    try:
        openai_key = getKeyValue("azure-openai-key") 
        client = OpenAI(api_key=openai_key) 
        await  updateProgress(progressmsg, "Generating image...", True, True)
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
        )

        url = response.data[0].url
        propsVar = {"imageurl": url}
        await  updateProgress(progressmsg, "Downloading image...", True, True)
        imageelem = cl.CustomElement(name="image",props=propsVar, display="inline")

        await cl.Message(content=prompt,elements=[imageelem]).send()
        await  updateProgress(progressmsg, "", False, True)
    except Exception as e:
        await  updateProgress(progressmsg, "There was an error generating image.", False, True)