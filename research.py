import requests
import chainlit as cl

async def performResearch(prompt):
    API_KEY = "lJHYg6jG2UZ1bse9VKaORP53zxQXt8WT"
    BASE_URL = "https://api.core.ac.uk/v3/search/works?q="+prompt

    params = {
        # "q": prompt,
        "limit": 10,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    response = requests.get(BASE_URL, headers=headers)
    props = {}
    if response.status_code == 200:
        
        data = response.json()
        count = len(data["results"])
        abstracts = []
        titles = []
        urls = []
        for article in data['results']:
            abstract = article['abstract']
            abstract = abstract[:300] + "..."
            abstracts.append(abstract)

            titles.append(article['title'])
            url = article['downloadUrl']
            url = url.replace("abs","pdf")
            urls.append(url)

        
        props = {"titles":titles,"abstracts":abstracts,"urls":urls, "count":count}
            
        elem = cl.CustomElement(name="Articles",props=props)
        await cl.Message(content="",elements=[elem]).send()
    else:
        await cl.Message(content="There was an error fetching the research articles").send()
