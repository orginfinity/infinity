
import asyncio
from common import *
import json
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

async def get_questions(questions):
    """Pretending to fetch data from linear"""
    return {
        "question1":questions["Q1"],
        "question2":questions["Q2"],
        "question3":questions["Q3"],
        "question4":questions["Q4"]
    }


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
