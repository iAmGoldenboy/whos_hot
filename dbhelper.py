__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_hot / dbhelper.py'
__datum__ = '29/01/17'

import pymysql
import dbconfig
import datetime

class DBHelper:

    def connect(self, database="NE_database"):
        return pymysql.connect(host="localhost",
                               user=dbconfig.db_user,
                               passwd=dbconfig.db_pass,
                               db=dbconfig.db_name)

    def add_rss_input(self, data):
        connection = self.connect()
        whattime = datetime.datetime.now()
        try:
            query = """INSERT IGNORE INTO rss_feeds(name, rssLink, avis, medietype, sektion)
            VALUES ({});""".format(data)
            print(query, whattime)

            with connection.cursor() as cursor:
                cursor.execute(query)
                connection.commit()
        except Exception as e:
            print(e)
        finally:
            connection.close()

    def get_all_feeds(self):
        connection = self.connect()
        try:
            query = """SELECT avis, sektion, medietype, rssLink, lastUpdate from rss_feeds ORDER BY medietype, avis, sektion; """
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("no feeds: ", e)
        finally:
            connection.close()

    def getHTMLtags(self, avis, block):
        connection = self.connect()
        try:
            query = "SELECT tagData from html_tags WHERE avis='{}' and tagArea='{}';".format(avis, block)
            # print(query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("no tag area: ", e)
        finally:
            connection.close()


    def getRSSlinks(self):
        """ used in fetchRSS
        :return:
        """
        connection = self.connect()
        try:
            query = """SELECT rssLink, avis, sektion, lastUpdate from rss_feeds ORDER BY lastUpdate; """
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("no feeds: ", e)
        finally:
            connection.close()