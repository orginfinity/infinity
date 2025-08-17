
import requests 
from common import *
google_search_uri = getKeyValue("google-search-uri")
google_fav_icons_uri = getKeyValue("google-fav-icons-uri")


async def getWebsitesProps(websites, titles, favicons, contents, thumbnails):
    # logger.info("Contents: %s", websites)
    """Pretending to fetch data from linear"""
    websitesProps = {}

    i = 0
    sourceCount = 0
    # for i in range(len(websites)):

    try:
        while i < len(websites):
            if (i < len(websites) and i < len(titles) and i < len(favicons) and i < len(contents) and i < len(
                    thumbnails)):
                websiteKey = "website" + str(i)

                contentsKey = "contents" + str(i)
                thumbnailKey = "thumbnail" + str(i)
                titlesKey = "titles" + str(i)
                faviconKey = "favicon" + str(i)

                if websites[i] != None and contents[i] != None and thumbnails[i] != None and titles[i] != None and \
                        favicons[i] != None:
                    # logger.info("WEBSITE : %s\n",websites[i])
                    websitesProps[websiteKey] = websites[i]
                    websitesProps[contentsKey] = contents[i]
                    websitesProps[thumbnailKey] = thumbnails[i]
                    websitesProps[titlesKey] = titles[i]
                    websitesProps[faviconKey] = favicons[i]
                    sourceCount += 1
            i += 1
    except Exception as e:
        print("Error while preparing websites props \n %s", e)
    finally:
        websitesProps["sourceCount"] = sourceCount

    return websitesProps


class imageFromGoogle:
    def __init__(self, link, displayLink, contextLink):
        self.link = link
        self.displayLink = displayLink
        self.contextLink = contextLink


def get_fav_icons(websites):
    # logger.info("to get icons: %s",websites)
    icons = []
    for website in websites:
        uri = google_fav_icons_uri + website + "&size=32"

        icons.append(uri)
    return icons


async def getImagesProps(images):
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
        print("Error while populating image props from Google\n%s", e)
    finally:
        imagesProps["imagesCount"] = imageCount

    return imagesProps


async def get_images_fromgoogle(prompt):
    try:
        uri = google_search_uri + prompt + "&searchType=image" + "&imgSize=medium"
        data = requests.get(uri).json()
        search_items = data.get("items")
        images = []

        for i, search_item in enumerate(search_items, start=1):
            content = ""
            imgObject = search_item.get("image")
            image = imageFromGoogle(search_item.get("link"), search_item.get("displayLink"),
                                    imgObject.get("contextLink"))

            if (image.link != None and image.contextLink != None and image.displayLink != None):
                images.append(image)
    except:
        print("Error while getting images from google:\n %s", len(images))
    finally:
        props = await getImagesProps(images)

    return props


async def get_websites_fromgoogle(prompt):
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

        if (search_items == None):
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
                if cse_thumbnail != None:
                    if len(cse_thumbnail) > 0:
                        cse_thumbnail = cse_thumbnail[0]
                        src = cse_thumbnail.get("src")
                        if src != None:
                            thumbnails.append(src)

            contents.append(content)
        favicons = get_fav_icons(websites)

    except Exception as e:
        print("Error while fetching websites from google \n%s", str(e))
    finally:
        props = await getWebsitesProps(websites, titles, favicons, contents, thumbnails)
        props["prompt"] = prompt

    return props


async def get_questionsProps(questions):
    props = {}
    try:
        if questions["Q1"] != None:
            props["question1"] = questions["Q1"]
        if questions["Q2"] != None:
            props["question2"] = questions["Q2"]
        if questions["Q3"] != None:
            props["question3"] = questions["Q3"]
        if questions["Q4"] != None:
            props["question4"] = questions["Q4"]

    except Exception as e:
        print("Exception while preparing questions props:\n%s", e)
    finally:
        return props
