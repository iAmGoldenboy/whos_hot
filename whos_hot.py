__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_hot / whos_hot.py'
__datum__ = '29/01/17'

from dbhelper import DBHelper
from flask import Flask
from flask import render_template
from flask import request
from model import gettingRSSes

import time

app = Flask(__name__)
DB = DBHelper()

@app.route("/")
def home():
    welcome = "Welcome to Python Flask Appss!"
    return render_template("base.html", title=welcome)

@app.route("/allFeeds")
def allFeeds():
    try:
        feeds = DB.get_all_feeds()
    except Exception as e:
        print("feed error: ", e)
        feeds = None
    # myline = "whats up"
    return render_template("feeds/allFeeds.html", data=feeds, overviewTitle="RSS Feeds in the system")


@app.route("/addRSSfeed", methods=['POST'])
def submitRSS():
    aname = request.form.get("aname")
    rssLink = request.form.get("rssLink")
    avis = request.form.get('avis')
    medietype = request.form.get('medietype')
    sektion = request.form.get('sektion')
    # lastUpdate = time.time()
    DB.add_rss_input("'{}', '{}', '{}', '{}', '{}'".format(aname, rssLink, avis, medietype, sektion))
    return allFeeds()
    # return render_template("addFeeds.html", overviewTitle="Add RSS feed")

@app.route("/entities")
@app.route("/entities/<namedEntity>")
def showEntities(namedEntity):
    return render_template("base.html", overviewTitle="Entities")

@app.route("/fetchRSS")
def fetchRSS():
    # pass
    feeds = DB.getRSSlinks()

    gettingRSSes(feeds)

    return render_template("base.html", overviewTitle="Jamming")



if __name__ == "__main__":
    app.run(port=5000, debug=True)

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