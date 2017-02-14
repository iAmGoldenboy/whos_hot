# -*- coding: utf-8 -*-
__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_hot / whos_hot.py'
__datum__ = '29/01/17'

from dbhelper import DBHelper
from flask import Flask
from flask import render_template, url_for
from flask import request
from bs4 import BeautifulSoup
import requests
import xmltodict
from model import gettingRSSes
import schedule
from time import sleep
import html5lib

from model_lib import URLSnotInDatabase
import time


app = Flask(__name__, static_folder='static')
start_time = time.time()
DB = DBHelper()

@app.route("/")
def home():
    welcome = "Welcome to Python Flask Appss!"
    return render_template("base.html", title=welcome, overviewTitle=welcome)

@app.route("/subdeck/here")
def here():
    welcome = "subdeck here!"
    return render_template("base.html", title=welcome, overviewTitle=welcome)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('base.html', title="Error {}".format(error), overviewTitle="Error {}".format(error)), 404

@app.route("/allFeeds")
def allFeeds():
    try:
        feeds = DB.getRSSlinks()
    except Exception as e:
        print("feed error: ", e)
        feeds = None
    # myline = "whats up"
    return render_template("feeds/allFeeds.html", data=feeds, title="RSS Feeds", overviewTitle="RSS Feeds i systemet")

@app.route("/fetchafeeds")
def fetchafeeds():

    output = "hej"

    feeds = None
    try:
        feeds = DB.getRSSlinks()
    except Exception as e:
        print("feed error: ", e)
        feeds = None

    output = [feed for feed in feeds[:2]]

    print("output 1", output)

    lookat = []
    for out in output:
        articleLink = out[0]
        avis = out[1]
        sektion = out[2]
        lookat.append([articleLink, avis, sektion])

    print("Lookat 1", lookat)

    knowarticles = []
    for look in lookat:
        feedR = requests.get(look[0])
        feedsDict = xmltodict.parse(feedR.content, process_namespaces=True)
        sleep(2)

        for rssItem in feedsDict["rss"]["channel"]["item"]:
            articleLink = rssItem["link"].replace("?referrer=RSS", "")
            print("article link", articleLink)
            knowarticles.append(articleLink)

    print("knownarticles 1", knowarticles)

    headlines = []
    for article in knowarticles[:4]:
        soup=""
        try:
            print("Trying to get soup")
            getLinkData = requests.get(article)
            soup = BeautifulSoup(getLinkData.content, "html5lib")
            print("Got soup -> ", soup.original_encoding, type(soup))

        except Exception as e:
            print("No soup", e)

        try:
            print("trying to get header")
            tagThing = ".article-header__title"
            print("TH", type(tagThing), tagThing)
            tagContent = soup.select(tagThing)
            tagContent_2 = soup.find_all(tagThing)
            print("tagcontent type", type(tagContent), tagContent_2)
            for item in tagContent:
                headlines.append(tagContent)
            print("tagContent 1", tagContent)
        except Exception as e:
            print("No tags", e,)

        sleep(3)

    print("Headlines 1", headlines)



    return render_template("feeds/fetchfeeds.html", output=output, lookat=lookat, knowarticles=knowarticles, headlines=headlines)

# @app.route("/addRSSfeed", methods=['POST'])
# def submitRSS():
#     aname = request.form.get("aname")
#     rssLink = request.form.get("rssLink")
#     avis = request.form.get('avis')
#     medietype = request.form.get('medietype')
#     sektion = request.form.get('sektion')
#     # lastUpdate = time.time()
#     DB.add_rss_input("'{}', '{}', '{}', '{}', '{}'".format(aname, rssLink, avis, medietype, sektion))
#     return allFeeds()
#     # return render_template("addFeeds.html", overviewTitle="Add RSS feed")


# @app.route("/hotte-navne")
# @app.route("/hotte-navne/")
# def hotteNavne():
#     #
#     translate = {"hour" : "timer", "day" : "dage", "minute" : "minuter"}
#
#
#     try:
#         intervalTime = request.args.get('tidsInterval', 24)
#         intervalTimeType  = request.args.get('tidsType', "HOUR")
#         inkluder = request.args.get("inkluderNavn", "")
#         ekskluder = request.args.get("ekskluderNavn", "")
#         getOnly = request.args.get("hentKun", "")
#         timeSpan = request.args.get("tidsRamme", "")
#         newsType = request.args.get("medieType", "")
#         sectionType = request.args.get("sektion", "") #indland, udland, kultur
#         newsOutlet = request.args.get("medieHus")
#         limit  = request.args.get('antal', 50)
#         baseURL = (request.base_url )
#     except Exception as e:
#         print("Hotte navne problem due to : ", e)
#         intervalTime = 15
#         intervalTimeType  = "HOUR"
#         limit  = 50
#         baseURL = request.base_url
#
#     userTip = """<strong class='userTip'>TIP:</strong> Du kan &aelig;ndre på <em class='userTip'>antal navne og tidsinterval</em> ved at lave din egen 's&oslash;gestreng'.
#      F.eks. vil <a href='{}?tidsType=HOUR&tidsInterval=3&antal=5' title='Lav din egen s&oslash;ning'>{}?tidsType=<em><strong>HOUR</em></strong>&tidsInterval=<em><strong>3</em></strong>&antal=<em><strong>5</em></strong></a> hente de 5 hotteste navne fra de seneste 3 timer.
#      Det er muligt at &aelig;ndre tidsType=<strong>HOUR</strong> til <strong>MINUTE</strong> eller <strong>DAY</strong>, samt tallet for <em>tidsInterval</em> og <em>antal</em>""".format(baseURL, baseURL)
#
#     title = "De {} Hotteste Navne de seneste {} {}.".format(limit, intervalTime, translate.get(str(intervalTimeType.lower()) ))
#
#     overviewTitle = "De {} <span class='overView'>Hotteste Navne</span> de seneste {} {}.".format(limit, intervalTime, translate.get(str(intervalTimeType.lower()) ))
#     # req_json = request.get_json()
#     # req_json_h = req_json['intervalTime']
#     # intervalTime=15, intervalTimeType="HOUR", limit=50
#     # string = timeType=Hour&timeValue=15
#
#     try:
#         feeds = DB.getHotNames(intervalTime, intervalTimeType, limit)
#         if len(feeds) == 0:
#             feeds = [["", "Ingen data - brug andet interval (f.eks. tidsInterval=HOUR) eller højere antal (f.eks. antal=15)"]]
#     except Exception as e:
#         print("feed error: ", intervalTime, intervalTimeType, limit, " --- due to : ", e)
#         feeds = []
#
#     barData = []
#     try:
#         barData = [feedItem[3] for feedItem in feeds]
#     except Exception as e:
#         print("no bar data due to : ", e)
#
#     return render_template("hotte_navne.html", data=feeds, userTip=userTip, title=overviewTitle,
#                            overviewTitle=overviewTitle, barChart=barData )

@app.route("/om-projektet")
def omProjektet():

    title = "Om projektet"

    overviewTitle = "Om projektet Hotte Navne"

    return render_template("om-projektet.html", title=title, overviewTitle=overviewTitle)


# @app.route("/entities/")
# # @app.route("/entities/<namedEntity>")
# def showEntities():
#
#     try:
#         neID = request.args.get('navn', 20019)
#         neName  = request.args.get('navnID', "Danmark")
#         limit  = request.args.get('antal', 50)
#         baseURL = (request.base_url )
#     except Exception as e:
#         print("Hotte navne problem due to : ", e)
#         neID = request.args.get('navn', 20019)
#         neName  = request.args.get('navnID', "Danmark")
#         limit  = 50
#         baseURL = request.base_url
#     print(neName, neID, limit)
#     try:
#         feeds = DB.getNamedEntity(neID, neName, limit)
#         if len(feeds) == 0:
#             feeds = [["", "Ingen data - brug andet interval (f.eks. tidsInterval=HOUR) eller højere antal (f.eks. antal=15)"]]
#     except Exception as e:
#         print("feed error: ", neName, neID, limit, " --- due to : ", e)
#         feeds = []
#
#     return render_template("entities.html", data=feeds, title=neName, overviewTitle="{} har {} entries".format(neName, len(feeds), baseURL))



# @app.route("/fetchRSS")
# def fetchRSS():
#     # pass
#     # feeds = DB.getRSSlinks()
#
#     # print(feeds)
#     gettingRSSes(outputFEEDURLS())
#
#     return render_template("base.html", overviewTitle="Jamming")



# def outputRSSLINKS():
#     return DB.getRSSlinks()
#
# def outputFEEDURLS():
#     rssLinks = outputRSSLINKS()
#     return URLSnotInDatabase(rssLinks)

# def processRSSes():
#
#     # pass
#     # feeds = DB.getRSSlinks()
#     # articlesToGet = URLSnotInDatabase(feeds)
#
#     # print(feeds)
#
#     with lock:
#         gettingRSSes(outputFEEDURLS())
#         print("Running periodic task!")
#         print("Elapsed time: " + str(time.time() - start_time))

# https://github.com/dbader/schedule
# def runningSchedule():
#     schedule.every(15.23456).minutes.do(processRSSes)
#     # schedule.every(1).minutes.do(fetchRSS())
#     # schedule.every(30).minutes.do(updatingSocialMedia)
#
#     while True:
#         schedule.run_pending()
#         sleep(1)

# def run_every_10_seconds():
#     print("Running periodic task!")
#     print("Elapsed time: " + str(time.time() - start_time))

if __name__ == "__main__":
    # runningSchedule()

    # t = Thread(target=runningSchedule)
    # t.start()
    # print("Start time: " + str(start_time))
    app.run(debug=True)












# /* if newSMcount > (previousSMcount * 2), then add to top of sharedCount que. */
# /addRSS / update /removeRSS
# field for name - rssLink - avis - sektion
#
# /addTagList /updateTagList / removeTagList
#
#
#
# /addAlias /removeAlias
# fields for NE - alias to be removed
# get from table namedEntities name = na** na** na**
#
#
# /article/link[], socialMedia[],
# show link to article, NEs, socialmedia graph,
# if link not in database: would you like us to fetch it and extract names?
#
#
# /NamedEntity/name[] (or alias), avis[], sektion[], date, dateRange[], graphTypes[]
# shows name (NE), aliases, list of articles + count, aviss + count, sektions + count
#
# /ListArticles/all, avis[], sektion[], date, dateRange[], graphTypes[]