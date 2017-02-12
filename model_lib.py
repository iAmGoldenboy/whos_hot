# -*- coding: utf-8 -*-
__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_hot / model_lib.py'
__datum__ = '10/02/17'

from dbhelper import DBHelper
import requests
import xmltodict
from time import sleep
import random
import string
from model_nlp import scrubString, pruneNECollection
from stats import quartiles
import dbconfig
from collections import Counter
import json

DB = DBHelper()

feeds = DB.getRSSlinks()

def URLSnotInDatabase(feeds):
    URLs2scrape = []
    seenlist = []
    remember = ""
    countess = 0


    for feedItem in sorted([[feed[2], feed[1], feed[0]] for feed in feeds]):
        print(feedItem, "COunt", countess)


        feedsDict = None

        try:
            feedR = requests.get(feedItem[2])
            feedsDict = xmltodict.parse(feedR.content, process_namespaces=True)
            if feedItem[1] == remember:
                # print("Same a before sleeping for 2 sec to not trash server")
                sleep(2)
            else:
                # print("NOT same as before, so only sleeping for 0.2, and moving quickly on")
                sleep(0.2)
            remember = feedItem[1]
        except Exception as e:
            print("No feed: ", e)

        # print(feedsDict)
        if feedsDict:
            # print("we have feed dict")
            try:
                for rssItem in feedsDict["rss"]["channel"]["item"]:
                    articleLink = rssItem["link"].replace("?referrer=RSS", "")
                    print("art link", articleLink)

                    ishere = DB.checkArticelLinkExistance(articleLink)

                    if len(ishere) == 0 and articleLink not in seenlist:
                        # then add to list
                        print(" ---> is here", len(ishere), articleLink)
                        try:
                            if feedItem[1] == "Berlingske Tidende":
                                # pass
                                print("dalink", articleLink[:len(articleLink)-2])
                                if articleLink[:len(articleLink)-2] in seenlist:
                                    print("in seenssss", articleLink)
                        except Exception as e:
                            print("Berlingeren", articleLink)
                        URLs2scrape.append([articleLink, feedItem[1], feedItem[0]])
                        seenlist.append(articleLink)

            except Exception as e:
                print("Bang! Not able to get go through feedsdict... due to ", e)

        countess += 1

    random.shuffle(URLs2scrape)
    # print("Will be going through ", len(URLs2scrape))
    # for feedURL in URLs2scrape:
    #     print("****   ", feedURL)
    return URLs2scrape


def extractHeaderText(item):
    """ Deals with missing periods after headline sentences, where there often is none,
    however sometimes there is a question mark or other character.
    :param item:
    :return: header string with a period after it (if it was missing).
    """

    headerText = ""

    try:
        if item.get_text().strip()[len(item.get_text().strip())-1] not in string.punctuation:
            headerText = "{}. ".format(scrubString(item.get_text().strip()))
        else:
            headerText = "{} ".format(scrubString(item.get_text().strip()) )
    except Exception as e:
        print("extractHeaderText error due to :", e)

    # print("header", headerText)
    return headerText


def extractImageText(imgtext, htmltag):
    """
    :param imgtext: the image text collected from the html tag
    :param htmltag: the html tag used to find image captions
    :return: a string without the 'Foto: Some Name'
    """

    imagetext = imgtext.get_text().strip()

    if "Foto:" in imagetext:

        try:
            imagetext = imagetext.split("Foto:")[0]

            if htmltag == 'billedtekstTag' and "REUTERS" in imagetext:
                imagetext = imagetext.split("REUTERS")[0]

        except Exception as e:
            print("No 'Foto:' data due to :", e)

    elif "Fotos:" in imagetext:

        try:
            imagetext = imagetext.split("Fotos:")[0]

        except Exception as e:
            print("No 'Fotos:' data due to :", e)

    elif "PHOTO:" in imagetext:

        try:
            imagetext = imagetext.split("PHOTO:")[0]

        except Exception as e:
            print("No 'PHOTO:' data due to :", e)

    elif "PHOTOS:" in imagetext:

        try:
            imagetext = imagetext.split("PHOTOS:")[0]

        except Exception as e:
            print("No 'PHOTOS:' data due to :", e)

    return imagetext





def get_social_metrics(url, pause=3):
    """ Collect the Social Media Metrics from sharedcount.com.
    :param url: the URL the we want to see how many Social Media encounters has.
    :param pause: time before continuing.
    :return: a dict with the various key/values.
    """
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

def extrapolateSocialMetrics(sharedCountDict):

    forDataBase = []
    for SoMeID, SoMeData in sharedCountDict.items():
        if isinstance(SoMeData, dict):
            # then we are in facebook
            for fbID, fbData in SoMeData.items():
                if fbData > 0 and fbID != "total_count":
                    forDataBase.append(["Facebook_{}".format(fbID), fbData])
        else:
            if SoMeData > 0:
                forDataBase.append([SoMeID, SoMeData])

    return forDataBase


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


def rePrune(namedEntityList):
    """ Deals with aggregated almost duplicates from bad coding!, uses the fuzzywuzzy library
    :param namedEntityList: a list of named Entities
    :return: a pruned collection (list)
    """
    toBePruned = [[num, ne] for ne, num in Counter(namedEntityList).items()]
    return pruneNECollection(toBePruned)

def keepThoseAboveQuartile(bagname, outputQuartiles=False):

    numlist = [num for id, num in Counter(rePrune(bagname)).items()]

    if len(numlist) >= 3:

        try:
            quarts = quartiles(numlist)
            okayedNE = {id:num for id, num in Counter(rePrune(bagname)).items() if num >= quarts[1]}
            if outputQuartiles == True:
                return okayedNE, quarts
            else:
                return okayedNE
        except Exception as e:
            print("Cant return those above quartile {} ... -> due to : {}".format(bagname[:3], e) )

    else:
        try:
            if outputQuartiles == True:
                return {id:num for id, num in Counter(rePrune(bagname)).items()}, None
            else:
                return {id:num for id, num in Counter(rePrune(bagname)).items()}
        except Exception as e:
            print("Cant return those above quartile {} ... -> due to : {}".format(bagname[:3], e) )


def signal(neList):

    seen = []
    shapeList = []
    outputDict = {}

    for namedEntity in neList:
        if namedEntity not in seen:

            # Build a list of binaries as signals, denoting presence (1) or absence (0)
            signalList = []

            for newitem in neList:

                if newitem == namedEntity:
                    signalList.append(1)
                else:
                    signalList.append(0)

            # No need to do the same thing for named entities that appear many times, so add it to a seen-list
            seen.append(namedEntity)

            # if there are more than three named entities (duplicates included) we can divide our list by three.
            if len(neList) >= 3:

                # Divide the list into three "equally" large chunks of head, torso and tail
                oneThird = int(round(len(neList)/3,0))
                head = signalList[:oneThird]
                torso = signalList[oneThird:(oneThird+oneThird)]
                tail = signalList[(oneThird+oneThird):]

                # Go through the sum of each chunk and describe it's shape (descending, ascending, diamond, hourglass, solid)
                if sum(head) < sum(torso) > sum(tail):
                    shape = "diamond"
                elif sum(head) >= sum(torso) > sum(tail):
                    shape = "descending"
                elif sum(head) > sum(torso) >= sum(tail):
                    shape = "descending"
                elif sum(head) < sum(torso) < sum(tail):
                    shape = "ascending"
                elif sum(head) < sum(torso) <= sum(tail):
                    shape = "ascending"
                elif sum(head) <= sum(torso) < sum(tail):
                    shape = "ascending"
                elif sum(head) > sum(torso) < sum(tail):
                    shape = "hourglass"
                elif sum(head) == sum(torso) == sum(tail):
                    shape = "solid"
                else:
                    # Adding a catch all, so far it has not been used...
                    shape = "unresolved!"

                # Add the shape to a list
                shapeList.append(shape)

                # If the named entity is seen more than once add to the output dict.
                if (sum(head) + sum(torso) + sum(tail) ) > 1:
                    outputDict[namedEntity] = {"sum" : (sum(head) + sum(torso) + sum(tail) ), "shape" : shape}
                else:
                    # Pass if 1 - need to keep noise down :)
                    pass

    # Also return a Counter object for the states. Not sure if I will use it.
    # !!! N.B. State Counter Object can be calculate vis SQL, no need to create an extra table !!!
    return outputDict
