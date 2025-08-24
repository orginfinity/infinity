import asyncio
from asyncio import as_completed
from concurrent.futures import ThreadPoolExecutor

from common import *

temperature = 0.9
api_type = "azure"
api_version = "2024-12-01-preview"
engine = "gpt-4o"
model = "gpt-4o"

system_content = "Do not ask any clarifying questions."
max_retries = 5
timeout = 30
debug = "true"

from collections import defaultdict
from database import *
messages = defaultdict(int)
project_client = None
agents_client = None
agent = None
from database import establishDbConnection, create_summary
establishDbConnection()

from googleClient import get_websites_fromgoogle
import json
openai_key = getKeyValue("azure-openai-key")
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key=openai_key)

async def callOpenAIForProject(prompt):
    try:
        prompt = "give me response in the following JSON format {\"Q0\":\"..\", \"Q1\":\"..\",\"Q2\":\"..\",\"Q3\":\"..\",\"Q4\":\"..\",\"Action0\":\"..\",\"Action1\":\"..\",\"Action2\":\"..\",\"Action3\":\"..\",\"Action4\":\"..\",\"Answer0\":\"..\", \"Answer1\":\"..\",\"Answer2\":\"..\",\"Answer3\":\"..\",\"Answer4\":\"..\"}. " \
                 "Q0 is the prompt given below. Q1,Q2,Q3 and Q4 are for the additional prompts you may want to suggest the user based on the prompt.Action0, Action1, Action2, Action3 and Action4 are the "\
                "tasks you would execute corresponding to the  prompts. You need to explain the action in atleast 3 sentences." \
                "Do not respond with questions but statements." \
                 " Do not ask any clarifying questions. Do not ask any personal questions about the user." \
                 "     Your prompt is this - " + prompt

        response = await client.chat.completions.create(
            model="gpt-4.1",
            messages = [{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    except Exception as e:
        print(str(e))
        return "Error while building follow up questions!\n%s"

async def callOpenAIForAnswer(prompt):
    try:
        openai_key = getKeyValue("azure-openai-key")
        # print(prompt)
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=openai_key)
        response = await client.chat.completions.create(
            model="gpt-4.1",
            messages = [{"role": "user", "content": prompt}]
        )
        print("returning answer")
        return response.choices[0].message.content

    except Exception as e:
        print(str(e))
        return "error"

class Result:
    def __init__(self):
        self.prompt = None
        self.stage = None
        self.correlationId = None
        self.sources = []
        self.favicons = []
        self.answer = None

async def performProject(prompt):
    try:
        questions = await callOpenAIForProject(prompt)
        questions = json.loads(questions)

        statusMsg = StatusMsg("statusmsg", "Identified 5 stages to perform")
        yield statusMsg

        results = list()

        futures = []
        try:
            for i in range(1):
                q = "Q" + str(i)
                stage = "Action" + str(i)
                question = questions[q]
                #
                answer = await callOpenAIForAnswer( question)
                websiteProps = await get_websites_fromgoogle( question)

                statusMsg = StatusMsg("statusmsg","Identified " + str(websiteProps["sourceCount"]) + " sources to analyze for stage " + str(i+ 1))
                yield statusMsg

                result =  Result()
                result.prompt = questions[q]
                result.stage = questions[stage]

                sources = []
                favicons = []
                for j in range(websiteProps["sourceCount"]):
                    sources.append(websiteProps["website"+str(j)])
                    favicons.append(websiteProps["favicon" + str(j)])

                result.sources = sources
                result.favicons = favicons
                result.answer = answer
                results.append(result)

                statusMsg = StatusMsg("statusmsg",f"stage {i+1} complete.")
                yield statusMsg

        except Exception as e:
            print(str(e))

            statusMsg = StatusMsg("statusmsg", "error")
            yield statusMsg

        #
        # statusMsg = StatusMsg("statusmsg", "done")
        # yield statusMsg

        statusMsg = StatusMsg("projectresult", results)
        yield statusMsg

    except Exception as e:
        print(str(e))
        statusMsg = StatusMsg("statusmsg", "error")
        yield statusMsg
 
 
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
  
async def conductProject(prompt,progressmsg):
    async for result in performProject(prompt):            
        try:
            if result.command == "statusmsg":
                if( result.result == "error"):
                    await asyncio.gather(updateProgress(progressmsg, result.result, False, True))
                else:
                    await asyncio.gather(updateProgress(progressmsg, result.result, True, True))
            elif result.command == "projectresult":
                await onProjectAnswer(result.result, prompt)
                await asyncio.gather(updateProgress(progressmsg, "Done", False, True))

        except Exception as ex:
            print(str(ex))
            await cl.Message(content = "There was an error. Please try again").send()