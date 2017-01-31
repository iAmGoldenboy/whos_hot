__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_hot / model.py'
__datum__ = '29/01/17'

import dbconfig
import json
import requests
import string
import xmltodict
from bs4 import BeautifulSoup
from collections import Counter
from time import sleep
from dbhelper import DBHelper
from model_nlp import collectNamedEntities, extractNE, getTagContent


DB = DBHelper()


def gettingRSSes(feedList):

    # print(feedList)
    counter = 0
    for feed in feedList:
        print("feed: ", counter, " - ", feed[0], feed[1])

        avis = feed[1]
        counter += 1
        feedsDict = None

        try:
            # print("trying to get feed")
            feedR = requests.get(feed[0])
            # print("got feed", feedR)
            feedsDict = xmltodict.parse(feedR.content, process_namespaces=True)
            # print("da dict", feedsDict)
        except Exception as e:
            print("No feed: ", e)

        if feedsDict:
            # articleLink = ""
            try:
                for feedItem in feedsDict["rss"]["channel"]["item"][:2]:

                    articleLink = feedItem["link"].replace("?referrer=RSS", "")
                    print(avis, articleLink)

                    getLinkData = requests.get(articleLink)
                    soup = BeautifulSoup(getLinkData.content, "lxml")

                    # htmlTagsList = ['overskriftTag', 'underrubrikTag', 'billedtekstTag', 'introTag', 'brodtextTag', 'mellemrubrikTag', 'quoteTag']

                    htmlTagsList = ['brodtextTag'] #, 'underrubrikTag', 'billedtekstTag', 'introTag', 'brodtextTag', 'mellemrubrikTag', 'quoteTag']

                    try:
                        tagItem = None
                        for htmltag in htmlTagsList:
                            # print("htmltag:", htmltag)
                            tagItem = DB.getHTMLtags(avis, htmltag)
                            print("Has tag", tagItem)

                            if tagItem:
                                tagOutput = []

                                try:

                                    for singleTag in tagItem[0]:
                                        tagContent = soup.select(singleTag)

                                        for item in tagContent:

                                            # print("Checking {}".format( item ))

                                            try:

                                                if htmltag == 'billedtekstTag':

                                                    imgtext = extractImageText(item, htmltag)

                                                    if imgtext not in tagOutput:
                                                        tagOutput.append(imgtext.replace("\n", "").replace("  ", ""))

                                                elif htmltag == "overskriftTag":

                                                    headerText = extractHeaderText(item.replace("\n", "").replace("  ", ""))
                                                    # print(headerText)

                                                    if headerText not in tagOutput:
                                                        tagOutput.append(headerText)

                                                elif htmltag == "brodtextTag":

                                                    broedText = item.get_text().strip().replace("\n", " ").replace("  ", "").replace('"', '').replace("”", "").replace("»", "").replace("«", "")

                                                    if broedText not in tagOutput:
                                                        if "Læs også" not in broedText \
                                                                or "/ritzau/" not in broedText \
                                                                or "Artiklen fortsætter under billedet" not in broedText\
                                                                or "Se også:" not in broedText:
                                                            tagOutput.append(broedText)

                                                else:
                                                    # print(item.get_text())
                                                    print(" end of file...: {} {}".format(singleTag, item.get_text().strip() ))  #, item.get_text().strip())
                                                    tagOutput.append(item.get_text().strip().replace("\n", "").replace("  ", "").replace("”", "").replace("»", "").replace("«", ""))

                                            except Exception as e:
                                                print("Item tagcontent problem due to : ", e)

                                    # print("TagOutput: {}: {}".format(singleTag, tagOutput) )
                                    try:
                                        for lines in tagOutput:
                                            # print("first NE's", extractNE(lines))

                                            try:
                                                tokenizeCleaned = getTagContent(lines)
                                                sentenceNEs = extractNE(tokenizeCleaned)
                                                if sentenceNEs:
                                                    # print("NE's         ", sentenceNEs)
                                                    print("NE's Count:  ", Counter(sentenceNEs))
                                                    # print("tokenline        : ", tokenizeCleaned)
                                                    # print("original line    : ", lines)
                                            except Exception as e:
                                                print("something went wrong here: ", e)


                                                # frequency distribution matrix- tertile

                                    except Exception as e:
                                        print("couldnt get NEs due to: ", e )

                                except Exception as e:
                                    print("Something went wrong : ", e)

                            else:
                                print("no tag")
                                print()

                    except Exception as e:
                        print("unable to get tagitem", e)



                    sleep(2.5)


            except Exception as e:
                print("Kaboom", e)

            #     update lastUpdated
        #         add links to database

        sleep(3)

def extractHeaderText(item):
    headerText = ""

    if item.get_text().strip()[len(item.get_text().strip())-1] not in string.punctuation:
        headerText = item.get_text().strip().replace("\n", "").replace("  ", "")
    else:
        headerText = item.get_text().strip().replace("\n", "").replace("  ", " ")

    return headerText


def extractImageText(imgtext, htmltag):

    imagetext = imgtext.get_text().strip()

    if "Foto:" in imgtext:

        try:
            imagetext = imgtext.get_text().strip().split("Foto:")[0]

            if htmltag == 'billedtekstTag' and "REUTERS" in imgtext:
                imagetext = imgtext.split("REUTERS")[0]

        except Exception as e:
            print("No 'Foto:' data due to :", e)

    elif "Fotos:" in imgtext:

        try:
            imagetext = imgtext.get_text().strip().split("Fotos:")[0]

        except Exception as e:
            print("No 'Fotos:' data due to :", e)

    return imagetext





def get_social_metrics(url, pause=3):
    api_key = dbconfig.apiKEY
    formalcall = "{}{}{}{}".format( 'https://free.sharedcount.com/?url=', url , '&apikey=' , api_key )

    dataDict = {}
    try:
        sharedcount_response = requests.get(formalcall)

        sleep(pause)

        if sharedcount_response.status_code == 200:
            data = sharedcount_response.text
            dataDict = dict(json.loads(data))
            return dataDict

    except Exception as e:
        print("Moving onwards due to", e)
        return dataDict


def getSocialCount(socialDict, spread=True):

    accumCount = 0
    if spread and socialDict is not None:
        # print(socialDict)

        try:
            for key, data in socialDict.items():
                if isinstance(data, int):
                    accumCount += data

                elif key == "Facebook":
                    accumCount += data.get("total_count")
        except Exception as e:
            print("Social Counter died:", e)

    # print(accumCount)
    return accumCount




# def getTagContent(soup, avis, block):
#
#     output = []
#
#     try:
#
#         tagData = DB.getHTMLtags(avis,block)
#         print(tagData[0])
#
#         for headTag in tagData[0]:
#             headlineContent = soup.select(headTag)
#             output.append(headlineContent[0].get_text().strip())
#             print("block", block, headlineContent[0].get_text().strip())
#             print("all__: ", headlineContent)
#     except Exception as e:
#         print("Could not get tag data due to: ", e)
#
#     return output