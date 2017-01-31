__author__ = 'Miklas Njor - iAmGoldenboy - http://miklasnjor.com'
__projectname__ = 'whos_hot / db_setup.py'
__datum__ = '29/01/17'

import pymysql
import dbconfig

connection = pymysql.connect(host='localhost',
                             user= dbconfig.db_user,
                             passwd=dbconfig.db_pass,
                             db = dbconfig.db_name
                             )

try:
    with connection.cursor() as cursor:
        try:
            sql = "CREATE DATABASE IF NOT EXISTS NE_database"
            cursor.execute(sql)
        except Exception as e:
            print("Cant create database due to: ", e)

        try:
            sql = """CREATE TABLE IF NOT EXISTS NE_database.rss_feeds (
id INT NOT NULL AUTO_INCREMENT,
name VARCHAR(30) NOT NULL UNIQUE,
rssLink VARCHAR(450) NOT NULL UNIQUE,
avis VARCHAR(40) NOT NULL,
medietype ENUM('Dagblad', 'Ugeblad', 'TV', 'Fagblad', 'Radio') NOT NULL,
sektion ENUM('Kultur', 'Indland', 'Udland', 'Sport', 'Økonomi', 'Politik', 'Debat') NOT NULL,
lastUpdate DATETIME,
PRIMARY KEY(`id`, `avis`)
) ENGINE=INNODB;


CREATE TABLE IF NOT EXISTS NE_database.html_tags (
id INT NOT NULL AUTO_INCREMENT,
avis VARCHAR(40) NOT NULL,
tagData VARCHAR(450) NOT NULL,
tagArea ENUM('overskriftTag', 'underrubrikTag', 'billedtekstTag', 'introTag', 'bylineTag', 'mellemrubrikTag', 'quoteTag', 'brodtextTag') NOT NULL,
dateAdded DATETIME,
PRIMARY KEY (`id`, `avis`),
FOREIGN KEY (`id`, `avis`)
    REFERENCES rss_feeds(`id`, `avis`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.articleLinks (
id INT NOT NULL AUTO_INCREMENT,
articleLink VARCHAR(450) NOT NULL UNIQUE,
date DATETIME,
sektion VARCHAR(40) NOT NULL,
avis VARCHAR(40) NOT NULL,
PRIMARY KEY(`id`, `articleLink`),
FOREIGN KEY (`id`)
    REFERENCES rss_feeds(`id`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=INNODB;


CREATE TABLE IF NOT EXISTS NE_database.articleSocialMediaCount (
id INT NOT NULL AUTO_INCREMENT,
articleLink VARCHAR(450) NOT NULL,
date DATETIME,
socialMediaID ENUM('FBTotal', 'FBLikes', 'FBShares', 'FBComments', 'Tweets', 'LinkedIn', 'Googleplus', 'Pins', 'Stumbles') NOT NULL,
socialMediaCount INT NOT NULL,
PRIMARY KEY(`id`, `articleLink`),
FOREIGN KEY (`id`, `articleLink`)
    REFERENCES articleLinks(`id`, `articleLink`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.namedEntities (
id INT NOT NULL AUTO_INCREMENT,
ne VARCHAR(60) NOT NULL UNIQUE,
aliases VARCHAR(60),
addedDate DATETIME,
PRIMARY KEY(`id`, `ne`)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.namedAliases (
id INT NOT NULL AUTO_INCREMENT,
alias VARCHAR(60) NOT NULL UNIQUE,
ne VARCHAR(60),
PRIMARY KEY(`id`, `alias`, `ne`),
FOREIGN KEY (`ne`)
    REFERENCES namedEntities(`ne`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.NE_Articles (
id INT NOT NULL AUTO_INCREMENT,
ne VARCHAR(60) NOT NULL,
articleLink VARCHAR(450) NOT NULL,
neOccuranceCount INT NOT NULL,
neOccurranceShape ENUM('descending', 'ascending', 'solid', 'diamond', 'hourglass'),
neOccuranceSpread INT, /* percent - from first to last encounter */
neDistanceFromTop INT, /* percent - first encounter */
neDistanceFromBottom INT, /* percent - last encounter */
PRIMARY KEY(`id`, `ne`, `articleLink`),
UNIQUE KEY `ne` (`ne`,`articleLink`),
FOREIGN KEY (`id`, `ne`)
    REFERENCES namedEntities(`id`, `ne`)
    ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (`id`, `articleLink`)
    REFERENCES articleLinks(`id`, `articleLink`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.foaf (
id INT NOT NULL AUTO_INCREMENT,
ne  VARCHAR(60) NOT NULL,
knows  VARCHAR(60) NOT NULL,
PRIMARY KEY (`id`, `ne`, `knows`),
UNIQUE KEY `ne` (`ne`,`knows`),
FOREIGN KEY (`id`,`ne`)
    REFERENCES namedEntities(`id`, `ne`)
    ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (`id`,`knows`)
    REFERENCES namedEntities(`id`, `ne`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.foaf_strong (
id INT NOT NULL AUTO_INCREMENT,
ne  VARCHAR(60)  NOT NULL,
knows  VARCHAR(60) NOT NULL,
articleLink VARCHAR(450) NOT NULL,
addedDate DATETIME,
PRIMARY KEY(`id`, `ne`, `knows`, `articleLink`),
UNIQUE KEY `ne` (`ne`,`knows`, `articleLink`),
FOREIGN KEY (`id`, `ne`)
    REFERENCES namedEntities(`id`, `ne`)
    ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (`id`,`knows`)
    REFERENCES namedEntities(`id`, `ne`)
    ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (`id`, `articleLink`)
    REFERENCES articleLinks(`id`, `articleLink`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=INNODB;"""
            cursor.execute(sql)
        except Exception as e:
            print(e)

    connection.commit()
except Exception as e:
    print("fuck", e)
finally:
    connection.close()
