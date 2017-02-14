# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import pymysql
import dbconfig

connection = pymysql.connect(host='localhost',
                             user= dbconfig.db_user,
                             passwd=dbconfig.db_pass,
                             db = dbconfig.db_name
                             )

try:
    with connection.cursor() as cursor:
        # try:
        #     sql = "CREATE DATABASE IF NOT EXISTS NE_database;"
        #     cursor.execute(sql)
        # except Exception as e:
        #     print("Cant create database due to: ", e)

        try:
            sql = """CREATE TABLE IF NOT EXISTS NE_database.rss_feeds (
rss_id INT NOT NULL AUTO_INCREMENT,
name VARCHAR(30) NOT NULL UNIQUE,
rssLink VARCHAR(450) NOT NULL UNIQUE,
avis VARCHAR(40) NOT NULL,
medietype ENUM('Dagblad', 'Ugeblad', 'TV', 'Fagblad', 'Radio') NOT NULL,
sektion ENUM('Kultur', 'Indland', 'Udland', 'Sport', 'Økonomi', 'Politik', 'Debat') NOT NULL,
lastUpdate DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY(`rss_id`, `avis`)
) ENGINE=INNODB;


CREATE TABLE IF NOT EXISTS NE_database.html_tags (
html_id INT NOT NULL AUTO_INCREMENT,
avis VARCHAR(40) NOT NULL,
tagData VARCHAR(450) NOT NULL,
tagArea ENUM('overskriftTag', 'underrubrikTag', 'billedtekstTag', 'introTag', 'bylineTag', 'mellemrubrikTag', 'quoteTag', 'brodtextTag') NOT NULL,
dateAdded DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY(`html_id`)
) ENGINE=INNODB;


CREATE TABLE IF NOT EXISTS NE_database.articleLinks (
article_id INT NOT NULL AUTO_INCREMENT,
articleLink VARCHAR(450) NOT NULL UNIQUE,
date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
sektion VARCHAR(40) NOT NULL,
avis VARCHAR(40) NOT NULL,
PRIMARY KEY(`article_id`)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.articleSocialMediaCount (
sm_id INT NOT NULL AUTO_INCREMENT,
date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
socialMedia_art_id INT NOT NULL,
socialMediaID ENUM(/*'Facebook_total_count',*/'Facebook_like_count', 'Facebook_share_count', 'Facebook_comment_count', 'Twitter', 'LinkedIn', 'GooglePlusOne', 'Pinterest', 'StumbleUpon') NOT NULL,
socialMediaCount INT NOT NULL,
PRIMARY KEY(`sm_id`),
FOREIGN KEY (`socialMedia_art_id`)
    REFERENCES articleLinks(`article_id`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.namedEntities (
ne_id INT NOT NULL AUTO_INCREMENT,
ne VARCHAR(60) NOT NULL UNIQUE,
addedDate DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY(`ne_id`, `ne`)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.namedAliases (
alias_id INT NOT NULL AUTO_INCREMENT,
alias_ne VARCHAR(60) NOT NULL UNIQUE,
original_ne_id INT,
addedDate DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY(`alias_id`, `alias_ne`, `original_ne_id`),
FOREIGN KEY (`original_ne_id`)
    REFERENCES namedEntities(`ne_id`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=INNODB;


/* CREATE UNIQUE INDEX ix_ReversePK ON  Auto2AutoFeature (auto_feature_id, auto_id); */
/* http://www.joinfu.com/2005/12/managing-many-to-many-relationships-in-mysql-part-1/ */

CREATE TABLE IF NOT EXISTS NE_database.namedEntity2Articles (
ne2art_id INT NOT NULL AUTO_INCREMENT,
ne2art_ne_id INT NOT NULL,
ne2art_art_id INT NOT NULL,
neOccuranceCount INT NOT NULL,
neOccuranceHead INT,
neOccuranceTail INT,
neOccurranceShape ENUM('descending', 'ascending', 'solid', 'diamond', 'hourglass'),
addedDate DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY(`ne2art_id`, `ne2art_ne_id`, `ne2art_art_id`) /* , */
/* UNIQUE KEY `ne2art_ne_id` (`ne2art_ne_id`,`ne2art_art_id`), */
/* FOREIGN KEY (`ne2art_ne_id`) */
/*    REFERENCES namedEntities(`ne_id`) */
/*    ON UPDATE CASCADE ON DELETE CASCADE, */
/* FOREIGN KEY (`ne2art_art_id`) */
/*    REFERENCES articleLinks(`article_id`) */
/*    ON UPDATE CASCADE ON DELETE CASCADE */
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS NE_database.foaf (
foaf_id INT NOT NULL AUTO_INCREMENT,
foaf_ne_id  INT NOT NULL,
foaf_knows_id  INT NOT NULL,
foaf_art_id INT NOT NULL,
addedDate DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
PRIMARY KEY (`foaf_id`),
FOREIGN KEY (`foaf_ne_id`)
    REFERENCES namedEntities(`ne_id`)
    ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (`foaf_art_id`)
    REFERENCES articleLinks(`article_id`)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=INNODB;

"""
            cursor.execute(sql)
        except Exception as e:
            print(e)

    connection.commit()
except Exception as e:
    print("fuck", e)
finally:
    connection.close()
