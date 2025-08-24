from common import *
import chainlit as cl
from googleClient import *
import asyncio
from followUpQuestions import *
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    MessageDeltaChunk,   
    MessageRole,
    MessageDeltaTextUrlCitationAnnotation,
    MessageDeltaTextContent, 
)
async def sendResponseMessage(prompt, progressmsg,  agents_client, agent, thread, thread2):
    try:
       
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

        response, result = await StreamAgentResponse(prompt,progressmsg,  agents_client, agent, thread, thread2)

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


async def StreamAgentResponse(prompt, progressmsg,   agents_client, agent, thread, thread2, forUris= False ):
    
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

async def conductSearch(prompt,progressmsg,  agents_client, agent, thread, thread2):
    try:
        files = cl.Message(content="",author="Infinity")
        await files.send()

        response, result = await sendResponseMessage(prompt, progressmsg,  agents_client, agent, thread, thread2)
        mainprompt = prompt

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