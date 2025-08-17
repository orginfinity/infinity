import database
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

# setupChat()

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
            await temp()
    except Exception as ex:
        print(str(ex))
import markdown
from xhtml2pdf import pisa

from io import BytesIO
from docx import Document
from html2docx import html2docx
@cl.on_chat_start


async def on_chat_start():
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

async def sendResponseMessage(prompt, progressmsg):
    try:
        global agents_client
        global logger
        sources_element_props = await get_websites_fromgoogle(prompt)
        images_element_props = await get_images_fromgoogle(prompt)

        showSpinner = True
        await asyncio.gather(updateProgress(progressmsg,"found sources...",showSpinner,True))
        headerMsg = cl.Message(content="", author="Infinity")
        if sources_element_props["sourceCount"] != 0 or images_element_props["imagesCount"] != 0:
            # headerProps = sources_element_props | images_element_props
            # headerProps["prompt"] = prompt

            await headerMsg.send()

        response, result = await StreamAgentResponse(prompt,progressmsg)

        if sources_element_props["sourceCount"] != 0 or images_element_props["imagesCount"] != 0:
            headerProps = sources_element_props | images_element_props
            Header = cl.CustomElement(name="Header", props=headerProps, display="inline")
            headerMsg.elements = [Header]
            # headerMsg = cl.Message(content="", elements=[Header], author="Infinity")
            await headerMsg.update()

        return response, result
    except Exception as e:
        await returnError()

        print(str(e))
        return False


async def StreamAgentResponse(prompt, progressmsg, forUris= False ):
    global project_client, agents_client, agent, thread, thread2

    try:
        tempthread = None
        if not forUris:
            tempthread = thread
        else:
            tempthread = thread2

        message = agents_client.messages.create(thread_id=tempthread.id,role=MessageRole.USER,content=prompt)
        result = ""
        rendering = False
        answerMsg = cl.Message(content="",  author="Infinity") 
        with agents_client.runs.stream(thread_id=thread.id, agent_id=agent.id) as stream:         
            for event_type, event_data, _ in stream:
                if isinstance(event_data, MessageDeltaChunk): 
                    if not forUris:
                        await answerMsg.stream_token(event_data.text)

                        if not rendering:
                            showSpinner = True
                            await asyncio.gather(updateProgress(progressmsg, "Rendering...",showSpinner, True))
                            rendering = True
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
        
            return result, True
    except Exception as e:
        return False


async def callOpenAI(prompt, progressmsg):

    try:
        showSpinner = True
        await asyncio.gather(updateProgress(progressmsg, "Identifying follow up sugegstions...", showSpinner, True))

        prompt = "give me response in the following JSON format {\"Q1\":\"..\",\"Q2\":\"..\",\"Q3\":\"..\",\"Q4\":\"..\"" \
         "Q1,Q2,Q3 and Q4 are for the additional prompts you may want to suggest the user based on the below prompt." \
        " Do not respond with questions but statements." \
         " Do not ask any clarifying questions. Do not ask any personal questions about the user." \
         "     Your prompt is this - " + prompt

        try:
            openai_key = getKeyValue("azure-openai-key")
            print("opan ai key is " + openai_key)
        except Exception as e:
            print("opan ai key is " + str(e))

        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        # client.api_key = openai_key
        response = client.responses.create(
            model="gpt-4.1",
            input=prompt
        )
        return response.output_text

    except Exception as e:
        print("Error while building follow up questions!\n%s", e)
        return None


async def sendFollowupQuestions(prompt,progressmsg):
    questions = await callOpenAI(prompt,progressmsg)

    try:
        questions = json.loads(questions)
        questions_element_props = await get_questions(questions)
        questions_element = cl.CustomElement(name="FollowUpQuestions", props=questions_element_props)
        msg = cl.Message(content="", elements=[questions_element], author="Infinity")
        await msg.send()
    except Exception as e:
        print(e)


# os.environ["OAUTH_GOOGLE_CLIENT_ID"] = getKeyValue("google-client-id")
# os.environ["OAUTH_GOOGLE_CLIENT_SECRET"] = getKeyValue("google-auth-secret")
# os.environ["CHAINLIT_AUTH_SECRET"] = getKeyValue("chainlit-secret")
# os.environ["CHAINLIT_ROOT_PATH"] = "/"

database.establishDbConnection()

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

async def onProjectAnswer(clientSummaries,mainprompt):
    try:
        count = 0
        propsVar = {}
        completeAnswer = ""
        for summary in clientSummaries:

            promptVar = "prompt" + str(count)
            actionVar = "action" + str(count)
            sourcesVar = "sources" + str(count)
            faviconVar = "favicon" + str(count)
            answerVar = "answer" + str(count)

            propsVar[promptVar] = summary.prompt
            propsVar[actionVar] = summary.stage

            sources = summary.sources
            formattedSources = [x.replace("'","\"") for x in sources]
            propsVar[sourcesVar] = formattedSources

            favicons = summary.favicons
            formattedFavIcons = [x.replace("'", "\"") for x in favicons]
            propsVar[faviconVar] = formattedFavIcons

            propsVar[answerVar] = summary.answer
            completeAnswer += summary.answer
            count += 1

        if count > 0:
            propsVar["promptactioncount"] = count
            propsVar["mainprompt"] = mainprompt
            propsVar["answer"] = completeAnswer

            ProjectElem = cl.CustomElement(name="Project", props=propsVar, display="inline")
            docxelem = await getDocxFile(mainprompt, completeAnswer)
            pdfElem = await getPDFFile(mainprompt, completeAnswer)
            mdElem = await getMDFile(mainprompt, completeAnswer)

            ProjectMsg = cl.Message(content="", elements=[docxelem,pdfElem,mdElem], author="Infinity")
            await ProjectMsg.send()

            ProjectMsg = cl.Message(content="", elements=[ProjectElem], author="Infinity")
            await ProjectMsg.send()

            ProjectMsg = cl.Message(content=completeAnswer,   author="Infinity")
            await ProjectMsg.send()

    except Exception as ex:
        #TODO: Signal to caller to cancel timer
        print(ex)

async def get_questions(questions):
    """Pretending to fetch data from linear"""
    return {
        "question1":questions["Q1"],
        "question2":questions["Q2"],
        "question3":questions["Q3"],
        "question4":questions["Q4"]
    }

async def updateIPBasedMsgCount():
    requests.post("http://localhost:8086/requestcount/ip")

async def updateEmailBasedMsgCount():
    email = cl.user_session.get("email")
    requests.post("http://localhost:8086/requestcount/email/" + email)

async def updateProgress(progressmsg,msg,showSpinner, shouldUpdate):

    propsVar = {"message": msg,"showSpinner":showSpinner}
    headerelem = progressmsg.elements[0]
    headerelem.props = propsVar

    if(shouldUpdate):
        await progressmsg.update()
    else:
        await progressmsg.send()

from database import *
from Project import *

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
    mode = cl.user_session.get("mode")

    if mode == None:
        mode = "search"
    showSpinner = True
    progreselem = cl.CustomElement(name="SimpleSearchProgress", display="inline")
    progressmsg = cl.Message(content="", elements=[progreselem], author="Infinity")
    await asyncio.gather(updateProgress(progressmsg, "Thinking...", showSpinner, False))

    mode = "search"
    if mode == "search":
        try:
            files = cl.Message(content="",author="Infinity")
            await files.send()

            response, result = await sendResponseMessage(prompt, progressmsg)
            mainprompt = message.content

            docxelem = await getDocxFile(mainprompt, response)
            pdfElem = await getPDFFile(mainprompt, response)
            mdElem = await getMDFile(mainprompt, response)
            files.elements = [docxelem,pdfElem,mdElem]
            await files.update()
            # await cl.Message(content="",elements=[docxelem,pdfElem,mdElem], author="Infinity").send()

            if result:
                await sendFollowupQuestions(prompt,progressmsg)
                await asyncio.gather(updateProgress(progressmsg, "Done.", False, True))

        except Exception as e:
            await cl.Message(content = "There was an error. Please try again").send()
            print("Error in OnMessage:\n%s",e)
    elif mode == "project":
        async for result in performProject(prompt):
            print(result.result)
            try:
                if result.command == "statusmsg":
                    if( result.result == "error"):
                        await asyncio.gather(updateProgress(progressmsg, result.result, False, True))
                    else:
                        await asyncio.gather(updateProgress(progressmsg, result.result, True, True))
                elif result.command == "projectresult":
                    await onProjectAnswer(result.result, message.content)
                    await asyncio.gather(updateProgress(progressmsg, "Done", False, True))

            except Exception as ex:
                print(str(ex))
                await cl.Message(content = "There was an error. Please try again").send()

    email = cl.user_session.get("email")

    try:
        if email == None:
            await updateIPBasedMsgCount()
        else:
            await updateEmailBasedMsgCount()

        if requestsnotfound:
            content = {"command": "getreqlimits", "status": "processing"}
            await cl.send_window_message(content)

    except Exception as ex:
        print(str(ex))

    cl.user_session.set("curReqCount", currentReqCount + 1)
    await asyncio.gather(updateProgress(progressmsg, "Done", False, True))


