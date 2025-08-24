
import requests 
import chainlit as cl

async def PerformNews( prompt=None):
    url = None    
    sources = "engadget,entertainment-weekly,espn,fortune,fox-news,google-news,ign"\
                "medical-news-today,msnbc,mtv-news,national-review,nbc-news,new-scientist,newsweek,"\
                "next-big-future,nfl-news,nhl-news,polygon,recode,reuters,techcrunch,the-hill,the-huffington-post,"\
                "the-next-web,the-verge,the-wall-street-journal,the-washington-post,the-washington-times,time,"\
                    "usa-today,vice-news,wired,al-jazeera-english,bbc-news,cnn,buzzfeed,business-insider,breitbart-news,"\
                        "bloomberg,bleacher-report,axios,associated-press,abc-news"
    
    baseurl = "https://newsapi.org/v2/everything?sortBy=date&apiKey=b7a13e76fec74b0fb8a124f511830a68"
    if prompt:
        url = baseurl + "&q="+ prompt
    else:
        url = baseurl

    url += "&sources=" + sources 
 
    response = requests.get(url)

    props = {}
    if response.status_code == 200:
        data = response.json()
        titles = []
        descriptions = []
        urls = []
        urlsToImage = []
        publishedOn = []
        articlecount = len(data["articles"]) 

        if articlecount == 0 and prompt != None:
            await cl.Message(content="No headlines found for your search query! Top headlines are...").send()
            await PerformNews()
            return
        elif prompt == None and len(data["articles"]) == 0:
            await cl.Message(content="No headlines found...").send()
            return
        else:
            for article in data['articles']:
                titles.append(article['title'])
                descriptions.append(article['description'])
                urls.append(article['url'])
                urlsToImage.append(article['urlToImage'])
                publishedOn.append(article['publishedAt'])

        props = {"count":articlecount, "publishedOn":publishedOn, "titles":titles,"descriptions":descriptions,"urls":urls, "urlsToImage":urlsToImage}
            
        elem = cl.CustomElement(name="News",props=props)
        await cl.Message(content="",elements=[elem]).send()
    else:
        await cl.Message(content="There was an error fetching the news").send()
