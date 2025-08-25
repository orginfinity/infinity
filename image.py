from openai import OpenAI
from common import getKeyValue
import chainlit as cl
async def performImage(prompt):
    
    openai_key = getKeyValue("azure-openai-key")
 
    client = OpenAI(api_key=openai_key) 
 
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
    )

    url = response.data[0].url
    propsVar = {"imageurl": url}
    imageelem = cl.CustomElement(name="image",props=propsVar, display="inline")

    await cl.Message(content=prompt,elements=[imageelem]).send()