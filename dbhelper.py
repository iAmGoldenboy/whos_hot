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


    def getNamedEntity(self, ne_id, neName, limit):


        connection = self.connect()
        try:
            query = """SELECT ne2art_ne_id AS NE_ID, ne, articleLink AS LINKS, sektion, avis, neOccuranceCount AS CO, neOccuranceTail AS CH, neOccuranceHead as CT, neOccurranceShape AS SHAPE, article_id AS A_ID, articleLinks.date AS DATE
                        FROM namedEntity2Articles
                        JOIN articleLinks
                            ON namedEntity2Articles.ne2art_art_id=articleLinks.article_id
                        JOIN namedEntities
                            ON namedEntity2Articles.ne2art_ne_id=namedEntities.ne_id
                        WHERE ne2art_ne_id = {}
                        GROUP BY ne, article_id, CO, CH, CT, SHAPE
                        ORDER BY article_id DESC
                        LIMIT {};""".format(ne_id, limit)

            print(query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("no tag area: ", e)
        finally:
            connection.close()



    def getHotNames(self, intervalTime=15, intervalTimeType="HOUR", limit=50):
        connection = self.connect()
        try:
            query = """SELECT ne2art_ne_id, ne, ne_id, COUNT(ne2art_ne_id)
            FROM namedEntity2Articles
            JOIN namedEntities
            ON namedEntity2Articles.ne2art_ne_id=namedEntities.ne_id
            WHERE namedEntity2Articles.addedDate >= now() - INTERVAL {} {}
            GROUP BY ne
            ORDER BY COUNT(*) DESC  LIMIT {};""".format(intervalTime, intervalTimeType, limit)
            # print(query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("no hot name due to: ", e)
        finally:
            connection.close()


    def getRSSlinks(self):
        """ used in fetchRSS
        :return:
        """
        connection = self.connect()
        try:
            query = """SELECT rssLink, avis, sektion, lastUpdate, rss_id, medietype from rss_feeds ORDER BY lastUpdate; """
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("no feeds: ", e)
        finally:
            connection.close()

    def checkArticelLinkExistance(self,articleLink):
        connection = self.connect()
        try:
            query = """select * from articleLinks where articleLink ="{}";""".format(articleLink)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("no feeds: ", e)
        finally:
            connection.close()

    def addNamedEntity(self, namedEntity):
        """ used in ...
        :param namedEntity:
        :return:
        """
        connection = self.connect()
        try:
            query = """INSERT INTO namedEntities(ne) VALUES('{}');""".format(namedEntity)
            print("insert NE -> ", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            connection.commit()
        except Exception as e:
            print("Error with named entity : ", e)
        finally:
            connection.close()

    def addNamedEntity_Article(self, namedEntity, articleLink, count, countType="neOccuranceCount" ):
        """ used in ...
        :param namedEntity:
        :return:
        """
        connection = self.connect()
        try:
            query = """INSERT INTO namedEntity2Articles(ne, articleLink, {}) VALUES('{}', '{}', {});""".format(countType, namedEntity, articleLink, count)
            print("addNamedEntity_Article : ", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            connection.commit()
        except Exception as e:
            print("Error with named entity {} : {}".format(namedEntity, e))
        finally:
            connection.close()

    def addNamedEntityFOAF(self, namedEntity, knows):
        """ used in ...
        :param namedEntity:
        :return:
        """
        connection = self.connect()
        try:
            query = """INSERT IGNORE INTO foaf(ne, knows) VALUES('{}', '{}');""".format(namedEntity, knows)
            # print("addNamedEntityFOAF : ", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            connection.commit()
        except Exception as e:
            print("Error with named entity {} -> {} : {}".format(namedEntity, knows, e))
        finally:
            connection.close()

    def updateNamedEntity_Article(self, namedEntity, articleLink, count, countType="neOccuranceHead"):
        """ used in ...
        :param namedEntity:
        :return:
        """
        connection = self.connect()
        try:
            query = """UPDATE namedEntity2Articles SET {}={} WHERE ne='{}' and articleLink='{}';""".format(countType, count, namedEntity, articleLink)
            # print("updateNamedEntity_Article : ", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            connection.commit()
        except Exception as e:
            print("Error with updateNamedEntity_Article {} / {} : {}".format(namedEntity, articleLink, e))
        finally:
            connection.close()


            # http://stackoverflow.com/questions/17459762/mysql-many-to-many-relationship-with-foreign-keys
            # INSERT INTO Films (Title) VALUES ('Title1');
            # SET @film_id = LAST_INSERT_ID();
            #
            # INSERT INTO Genres (Name) VALUES ('Genre1');
            # SET @genre_id = LAST_INSERT_ID();
            #
            # INSERT INTO Films_Genres (film_id, genre_id) VALUES(@film_id, @genre_id);




    def insertArticleLink(self, articleLink, sektion, avis):
        """ Inserts the articleLink, section and newspaper name into articleLinks
        :param articleLink: URL to the article
        :param sektion: Section of the paper
        :param avis: Newspaper Name
        :return: returns articleLink_id
        """

        connection = self.connect()
        try:
            query = """INSERT INTO articleLinks (articleLink, sektion, avis) VALUES ('{}', '{}', '{}');""".format(articleLink, sektion, avis)
            print("insert articleLink", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
                lastID = cursor.lastrowid
            connection.commit()
            if lastID == 0:
                try:
                    lastID = self.getItemID('article_id', 'articleLinks', 'articleLink', articleLink)[0][0]
                except Exception as e:
                    print("Couldn't get hold of id for article: {} -> due to : {}".format(articleLink, e))
            return lastID
        except Exception as e:
            print("Error with articleLinks: {} {} {} due to : {}".format(articleLink, sektion, avis, e))
        finally:
            connection.close()

    def insertNamedEntity(self, ne):
        # ne_id INT NOT NULL AUTO_INCREMENT,
        # ne VARCHAR(60) NOT NULL UNIQUE,
        connection = self.connect()
        try:
            query = """INSERT INTO namedEntities (ne) VALUES ('{}');""".format(ne)
            print("insertNamedEntity -> " , query)
            with connection.cursor() as cursor:
                cursor.execute(query)
                lastID = cursor.lastrowid
            connection.commit()
            if lastID == 0:
                try:
                    lastID = self.getItemID('ne_id', 'namedEntities', 'ne', ne)[0][0]
                except Exception as e:
                    print("Couldn't get hold of id for namedEntity: {} -> due to : {}".format(ne, e))
            return lastID
        except Exception as e:
            print("Error with ne: {} due to : {}".format(ne, e))
        finally:
            connection.close()

    def insertSocialMedia(self, article_id, enumValue, count):

        connection = self.connect()
        try:
            # query = """INSERT INTO articleSocialMediaCount (socialMedia_art_id, socialMediaID, socialMediaCount)
            # VALUES ({}, '{}', {});""".format(article_id, enumValue, count)
            query = """INSERT INTO articleSocialMediaCount (socialMedia_art_id, socialMediaID, socialMediaCount)
            SELECT * FROM (SELECT {}, '{}', {}) AS tmp
            WHERE NOT EXISTS (
                SELECT socialMedia_art_id, socialMediaID, socialMediaCount FROM articleSocialMediaCount WHERE socialMedia_art_id = {} AND socialMediaID = '{}' AND socialMediaCount = {}
            ) LIMIT 1;""".format(article_id, enumValue, count, article_id, enumValue, count)
            print("insertSocialMedia -> ", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            connection.commit()
        except Exception as e:
            print("Error with {} / {} / {} : {} due to : {}".format(article_id, enumValue, count, e))
        finally:
            connection.close()

    def getItemID(self,id_key, table, id_field, item, multiple=False):
        """ Gets the ID (primary key) for the item in question.
        :param id_key: i.e. 'article_id'
        :param table: i.e. <table> 'articleLinks
        :param id_field: i.e <other fields to look in> 'articlelink' or 'ne'
        :param item: i.e. 'articleLink'
        :return:
        """

        connection = self.connect()
        try:
            if multiple == False:
                query = """SELECT {} FROM {} WHERE {}='{}'; """.format(id_key, table, id_field, item)
            else:
                query = """SELECT {}, {} FROM {} WHERE {} = {} AND {} = {};""".format(id_field[0], id_field[1], table, id_field[0], item[0], id_field[1], item[1] )
            # SELECT ne_id FROM namedEntities WHERE ne='some name';

            print("getItemID", query)
            with connection.cursor() as cursor:
                cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print("no where :) to be found due to : ", id_key, table, id_field, item, e)
        finally:
            connection.close()

    def insertValuesReturnID(self, tableName, tableFields, values, lookFor, item2look4, item_id='', mode="single", returnID=False, printQuery=False):
        """ Insert values to the database, and returns the row_id if returnID = True
        http://stackoverflow.com/questions/3164505/mysql-insert-record-if-not-exists-in-table?rq=1
        :param tableName:   Name of the table
        :param tableFields: List of fields you want to insert into
        :param values:      List of values you want to insert into the fields
        :param lookFor:     What to look for in table, typically 'ne' or 'name' type of value
        :param item2look4:  Item to look for, typically 'some ne' or 'real name' WHERE lookfor = item2look4
        :param item_id:     Used to return the id_row, i.e. 'ne_id' or 'article_id'. Default empty.
        :param returnID:    Should the function return a row_id of what that has just been updated.
        :return:            The row_id of what that has just been updated, if returnID=True
        """

        newvalues = ""
        for value in values:
            if isinstance(value, int):
                newvalues += "{},".format(value)
            elif isinstance(value, str):
                newvalues += "'{}',".format(value)
        newvalues = newvalues[:len(newvalues)-1]
        tableFields = ", ".join(tableFields)
        # print(tableFields)


        connection = self.connect()

        try:
            multiple = False
            if mode == "single":
                query = """INSERT INTO {} ({})
            SELECT * FROM (SELECT {}) AS tmp
            WHERE NOT EXISTS (
                SELECT {} FROM {} WHERE {} = '{}'
            ) LIMIT 1;""".format(tableName, tableFields, newvalues, lookFor, tableName, lookFor, item2look4)

            elif mode == "ne2art":
                # table: namedEntities2articles
                query = """INSERT IGNORE INTO {} ({}) VALUES ({});""".format(tableName, tableFields, newvalues)

            elif mode == "foaf":
                # table: foaf
                query = """INSERT INTO {} ({})
            SELECT * FROM (SELECT {}) AS tmp
            WHERE NOT EXISTS (
                SELECT {}, {} FROM {} WHERE {} = {} AND {} = {}
            ) LIMIT 1;""".format(tableName, tableFields, newvalues, lookFor[0], lookFor[1], tableName, lookFor[0], item2look4[0], lookFor[1], item2look4[1])
                multiple = True

            print("insertValuesReturnID ----> ", query )
            if printQuery == True:
                print(query)

            with connection.cursor() as cursor:
                cursor.execute(query)
                lastID = cursor.lastrowid
            connection.commit()

            if returnID == True:
                if lastID == 0:
                    try:
                        lastID = self.getItemID(item_id, tableName, lookFor, item2look4, multiple=multiple)[0][0]
                    except Exception as e:
                        print("Couldn't get hold of id: {} for {}: {} -> due to : {}".format(item_id, tableName, item2look4, e))
                return lastID

        except UnicodeError as e:

            print("Unicode error. Trying alternative insertion. The error is with table: {} fields: {} values: {} lookfor: {} item: {} due to : {}".format(tableName, tableFields, values, lookFor, item2look4, e))

            try:
                # Yay, works! -ish :(
                query = """INSERT INTO {} ({})
            SELECT * FROM (SELECT {}) AS tmp
            WHERE NOT EXISTS (
                SELECT {} FROM {} WHERE {} = '{}'
            ) LIMIT 1;""".format(tableName, tableFields, newvalues.encode('latin-1', 'ignore').decode('latin-1'), lookFor, tableName, lookFor, item2look4.encode('latin-1', 'ignore').decode('latin-1'))

                if printQuery == True:
                    print(query)

                with connection.cursor() as cursor:
                    cursor.execute(query)
                    lastID = cursor.lastrowid
                connection.commit()

                if returnID == True:
                    if lastID == 0:
                        try:
                            lastID = self.getItemID(item_id, tableName, lookFor, item2look4.encode('latin-1', 'ignore').decode('latin-1'))[0][0]
                        except Exception as e:
                            print("Couldn't get hold of id: {} for {}: {} -> due to : {}".format(item_id, tableName, item2look4.encode('latin-1', 'ignore').decode('latin-1'), e))
                    return lastID

                print("Alternative insertion worked for orig {} -> {}".format(newvalues, newvalues.encode('latin-1', 'ignore').decode('latin-1')))

            except Exception as e:
                print("Converting to Latin-1 didn't work with table: {} fields: {} values: {} lookfor: {} item: {} due to : {}".format(tableName, tableFields, values, lookFor, item2look4, e))


        except Exception as e:
            print("Error with table: {} fields: {} values: {} lookfor: {} item: {} due to : {}".format(tableName, tableFields, values, lookFor, item2look4, e))
        finally:
            connection.close()





