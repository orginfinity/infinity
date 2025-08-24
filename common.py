from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import chainlit as cl

import markdown
from xhtml2pdf import pisa
from io import BytesIO
from docx import Document
from html2docx import html2docx

secrets = {}
secrets["google-search-uri"] = None
secrets["google-fav-icons-uri"] = None
secrets["agent-uri"] = None
secrets["sqlloginpwd"] = None
secrets["google-auth-secret"] = None
secrets["google-client-id"] = None
secrets["chainlit-secret"] = None
secrets["azure-openai-key"] = None

class StatusMsg:
    def __init__(self,command,result):
        self.command = command
        self.result = result

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


import markdown
async def getDocxFile(mainprompt, md_content):
    md_content += "## **" + mainprompt + "**"
    html_content_bytes = markdown.markdown(md_content)

    buf = html2docx(html_content_bytes, title="My Document")
    fileelem = cl.File(
        name= mainprompt + ".docx",
        content=buf.getvalue(),
        # content=doc_stream.getvalue(),
        display="inline"
    )

    return fileelem


async def getPDFFile(mainprompt, md_content):
    md_content += "## **" + mainprompt + "**"
    html_content = markdown.markdown(md_content)

    pdf_bytes = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_bytes)
    fileelem = cl.File(
        name= mainprompt + ".pdf",
        content=pdf_bytes.getvalue(),
        # content=doc_stream.getvalue(),
        display="inline"
    )

    return fileelem

async def getMDFile(mainprompt, md_content):
    md_content += "## **" + mainprompt + "**"
    fileelem = cl.File(
        name= mainprompt + ".md",
        content=md_content,
        # content=doc_stream.getvalue(),
        display="inline"
    )

    return fileelem


async def returnError():
    image = cl.Image(path="./maintenance.gif", name="image1", display="inline") 
    await cl.Message(
            content="There was an error establishing session. We are on it!",
            # elements=[image],
        ).send()

async def updateProgress(progressmsg,msg,showSpinner, shouldUpdate):

    propsVar = {"message": msg,"showSpinner":showSpinner}
    headerelem = progressmsg.elements[0]
    headerelem.props = propsVar

    if(shouldUpdate):
        await progressmsg.update()
    else:
        await progressmsg.send()