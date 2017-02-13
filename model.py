# -*- coding: utf-8 -*-
__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_hot / model.py'
__datum__ = '29/01/17'

import requests
from bs4 import BeautifulSoup
from time import sleep
from dbhelper import DBHelper
from model_nlp import extractNE, removeStopwordsFromString
from model_lib import extractHeaderText, extractImageText, extrapolateSocialMetrics, signal, keepThoseAboveQuartile, get_social_metrics
from threading import Lock

DB = DBHelper()
lock = Lock()


def gettingRSSes(articlesToGet):

    # print("getting these", articlesToGet)

    counter = 0

    with lock:
        for feed in articlesToGet:
            print("feed: ", counter, " - ", feed[0], feed[1], feed[2])

            articleLink = feed[0]
            avis = feed[1]
            sektion = feed[2]


            try:
                # save the article link in the database and get the article_id for future use.
                article_id = DB.insertValuesReturnID('articleLinks', ['articleLink', 'sektion', 'avis'], [str(articleLink), str(sektion), str(avis)], 'articleLink', articleLink, 'article_id', returnID=True, printQuery=False)

                getLinkData = requests.get(articleLink)
                soup = BeautifulSoup(getLinkData.content, "lxml")

                htmlTagsList = ['overskriftTag', 'underrubrikTag', 'billedtekstTag', 'introTag', 'brodtextTag', 'mellemrubrikTag', 'quoteTag']

                try:
                    tagItem = None

                    NEbag = []
                    NEhead = []
                    NEtail = []

                    for htmltag in htmlTagsList:

                        # Get the htmltags for this newspaper
                        tagItem = DB.getHTMLtags(avis, htmltag)

                        if tagItem:
                            tagOutput = []

                            try:
                                # xtract text from each tagType.
                                for singleTag in tagItem[0]:
                                    tagContent = soup.select(singleTag)

                                    for item in tagContent:
                                        try:
                                            if htmltag == 'billedtekstTag':
                                                imgtext = extractImageText(item, htmltag)

                                                if imgtext not in tagOutput:
                                                    tagOutput.append(imgtext.replace(" og ", ", ").replace(" fra ", ", ").replace(" på ", ", ").replace(" til ", ", ").replace("\n", "").replace("  ", ""))

                                            elif htmltag == "overskriftTag":
                                                headerText = extractHeaderText(item.replace(" og ", ", ").replace(" fra ", ", ").replace(" på ", ", ").replace(" til ", ", ").replace("\n", "").replace("  ", ""))

                                                if headerText not in tagOutput:
                                                    tagOutput.append(headerText)

                                            elif htmltag == "brodtextTag":
                                                broedText = item.get_text().strip().replace(" og ", ", ").replace(" fra ", ", ").replace(" på ", ", ").replace(" til ", ", ").replace("\n", " ").replace("  ", "")

                                                if broedText not in tagOutput:
                                                    if "Læs også" not in broedText  or "/ritzau/" not in broedText or "Artiklen fortsætter under billedet" not in broedText or "Se også:" not in broedText:
                                                        tagOutput.append(broedText)

                                            else:
                                                otherText = item.get_text().strip().replace(" og ", ", ").replace(" fra ", ", ").replace(" på ", ", ").replace(" til ", ", ").replace("\n", " ").replace("  ", "")

                                                if otherText not in tagOutput:
                                                    tagOutput.append(otherText)

                                        except Exception as e:
                                            pass

                                # OK, now we have a list of sentences to go through. Let's do it!
                                try:
                                    for lines in tagOutput:
                                        try:
                                            # Remove stopwords and tokenize
                                            tokenizeCleaned = removeStopwordsFromString(lines)

                                            # Extract named entities for the sentences.
                                            sentenceNEs = extractNE(tokenizeCleaned)

                                            # If we have sentences to go through...
                                            if sentenceNEs:
                                                # ... add all to one big bag
                                                [NEbag.append(neToken) for neToken in sentenceNEs]

                                                # Lets also split between bodycopy and headercopy (inkl. captions)
                                                # When dealing with bodycopy, inline headlines and quotes add them to the NEtail list.
                                                if htmltag == "brodtextTag" or htmltag == "mellemrubrikTag" or htmltag == "quoteTag":
                                                    [NEtail.append(neToken) for neToken in sentenceNEs]

                                                # ... else they must be Header Copy and will be added to NEhead list
                                                else:
                                                    [NEhead.append(neToken) for neToken in sentenceNEs]

                                        except Exception as e:
                                            pass

                                            # frequency distribution matrix- tertile

                                except Exception as e:
                                    print("couldnt get NEs due to: ", e )

                            except Exception as e:
                                print("Something went wrong : ", e)
                        else:
                            # print("entering the else clause...", feed[0], feed[1], feed[2], articleLink, "art_id", article_id, "tag", htmltag, "counter", counter, "tagitem", tagItem)
                            pass


                    # OK, good! Now we have three list with NE's. Lets start adding them to the database.

                    # Lets first see what's in them
                    print("Shebang", NEbag)
                    # print("Signals NE", signal(NEbag))
                    # print("Signals Shape", signal(NEbag))
                    # Nice! Lets see if we can get some data or numbers
                    # print("NE BAG ALL COUNT:  ", keepThoseAboveQuartile(NEbag)) #, "\n", Counter(rePrune(NEbag)))
                    # print("Signals HEAD", signal(NEhead))
                    # print("NE BAG HEAD COUNT: ", keepThoseAboveQuartile(NEhead)) #, "\n",  Counter(rePrune(NEhead)))
                    # print("Signals TAIL", signal(NEtail))
                    # print("NE BAG TAIL COUNT: ", keepThoseAboveQuartile(NEtail)) #, "\n", Counter(rePrune(NEtail)) )

                    keepAll = signal(NEbag)
                    # for kNE in keepAll:
                    #     try:
                    #         testUnicode(kNE)
                    #     except Exception as e:
                    #         print("ee", kNE, e)

                    keepHead = keepThoseAboveQuartile(NEhead)
                    keepTail = keepThoseAboveQuartile(NEtail)

                    # Go through all items and collect: count, headcount, tailcount, shape and article id.
                    # Create a foaf list.
                    # Insert each named entitiy in the database and get the ne_id, add all of it to a dict.

                    collectNEdict = {}
                    foafDict = {}

                    fakeCounter = 0

                    for neID, neData in keepAll.items():

                        headCount, tailCount = 0, 0

                        try:
                            headCount = keepHead[neID]
                        except Exception as e:
                            # pass
                            print("1 ikke fundet", e, keepHead)

                        try:
                            tailCount = keepTail[neID]
                        except Exception as e:
                            # pass
                            print("2 ikke fundet", e, keepTail)

                        # ne_id = DB.insertNamedEntity(neID)
                        # Insert named entity into database
                        neValues = [str(neID)]
                        neoutput = DB.insertValuesReturnID('namedEntities', ['ne'], neValues, 'ne', neID, 'ne_id', mode="single", returnID=True, printQuery=True)

                        ne2artFields = ['ne2art_ne_id', 'ne2art_art_id', 'neOccuranceCount', 'neOccuranceHead', 'neOccuranceTail', 'neOccurranceShape']
                        nerartValues = [neoutput, article_id, neData.get("sum"), headCount, tailCount, str(neData.get("shape"))]

                        ne2art_output = DB.insertValuesReturnID('namedEntity2Articles', ne2artFields, nerartValues, ['ne2art_ne_id', 'ne2art_art_id'], [neoutput, article_id], 'ne_id',  mode="ne2art", returnID=True, printQuery=False)

                        # so update each ne and get row id, add ne and row_id to dict
                        collectNEdict[neID] = {"ne_id" : neoutput,
                                               "foaf_art_id": article_id,
                                               "foaflist": [neT for neT in keepAll.keys() if neID != neT] }

                        fakeCounter += 1

                    foafFields = ['foaf_ne_id', 'foaf_knows_id', 'foaf_art_id']
                    foafLookfor = ['foaf_ne_id', 'foaf_art_id']

                    for neID, neData in collectNEdict.items():
                        for foaf in neData.get("foaflist"):
                            foafValues = [neData.get("ne_id"), collectNEdict[foaf].get("ne_id"), neData.get("foaf_art_id")]
                            foaf_id = DB.insertValuesReturnID('foaf', foafFields, foafValues, foafLookfor, [neData.get("ne_id"), neData.get("foaf_art_id")], returnID=True, mode="foaf", printQuery=True)
                            print(neID, neData, foaf, foaf_id)
                    # Collect Social Media data
                    smDict = get_social_metrics(articleLink, pause=1)

                    # Add social media data into a list
                    SoMeCounter = extrapolateSocialMetrics(smDict)

                    # if there is data, add it to the database
                    SoMeCount = 0
                    if len(SoMeCounter) > 0:
                        for SoMes in SoMeCounter:
                            # update database with article_id, enum value, SoMe count.
                            DB.insertSocialMedia(article_id, SoMes[0], SoMes[1])
                            SoMeCount += SoMes[1]

                    print("Newspaper: {} / Sektion: {} / URL: {}".format(avis, sektion, articleLink) )
                    print("Article ID: {} / No. of NEs: {} / No. of SoMe Instances: {} / SoMe count: {}".format(article_id, len(keepThoseAboveQuartile(NEbag)), len(SoMeCounter), SoMeCount) )

                except Exception as e:
                    print("unable to get tagitem", e)

                # sleep(2.5)
            except Exception as e:
                print("SOMEthing went wrong due to   :   ", e)
            print()

            counter += 1

            sleep(2.5)


