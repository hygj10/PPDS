import json
from pprint import pprint

import pymysql
import requests
from bs4 import BeautifulSoup

BLOOMBERG_URL = "https://www.bloomberg.com/search?query="
companies = ["Google", "Apple", "Snapchat", "Bloomberg"]


class Spider:
    def __init__(self):
        self._key1 = "c31155fb4ef44e598697433926e764ae"
        self._key2 = "01572def178342179993aa4eef97d341"
        self._sentiment_analysis_endpoint = "https://eastus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment?Subscription-Key={key}" \
            .format(key=self._key2)

    def _create_database(self):

        connection = pymysql.connect(host='34.235.205.203',
                                     user='root',
                                     password='dwdstudent2015',
                                     db='ArticlesSentiment',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)

        create_db_query = "CREATE DATABASE IF NOT EXISTS ArticlesSentiment DEFAULT CHARACTER SET 'utf8'"
        cursor = connection.cursor()
        cursor.execute(create_db_query)
        cursor.close()

        connection.close()

    def _create_table(self):
        connection = pymysql.connect(host='34.235.205.203',
                                     user='root',
                                     password='dwdstudent2015',
                                     db='ArticlesSentiment',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)

        query = "CREATE TABLE IF NOT EXISTS ArticlesSentiment.Articles(company VARCHAR(255), article_url VARCHAR(400), score DOUBLE, PRIMARY KEY (company, article_url)); "
        cursor = connection.cursor()
        cursor.execute(query)
        cursor.close()

        connection.close()

    def __get_sentiment(self, story):
        payload = {'documents': [{'id': 1, 'language': 'en', 'text': story}]}
        print(json.dumps(payload))
        # headers = {'Ocp-Apim-Subscription-Key': self._key1}
        url = self._sentiment_analysis_endpoint
        result = requests.post(url, data=json.dumps(payload))
        json_result = json.loads(result.text)

        try:
            return json_result.get("documents")[0].get("score")
        except:
            return 0


    def get_links(self, company):
        return_array = []
        url = BLOOMBERG_URL + company
        body = requests.get(url)
        content = body.text

        soup = BeautifulSoup(content, "html.parser")

        story_links = soup.find_all("h1", {"class": "search-result-story__headline"})

        for link in story_links:
            return_array.append(link.contents[1]["href"])

        return return_array

    def get_content(self, company):

        links = self.get_links(company)
        return_content = dict()
        for link in links:
            content = requests.get(link).text
            soup = BeautifulSoup(content, "html.parser")
            story = ""
            paragraphs = soup.find_all("p")
            paragraphs = paragraphs[2:]
            for index, paragraph in enumerate(paragraphs):
                if index > 2:
                    try:
                        story += paragraph.contents[0]
                        story += "\n"
                    except:
                        continue

            return_content[link] = story
        return return_content

    def get_sentiments(self):

        self._create_database()
        self._create_table()

        connection = pymysql.connect(host='34.235.205.203',
                                     user='root',
                                     password='dwdstudent2015',
                                     db='ArticlesSentiment',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()

        for company in companies:

            stories = self.get_content(company=company)
            stories = dict(stories)

            for key in stories.keys():
                if key is not None:
                    story = stories.get(key)
                    score = self.__get_sentiment(story)
                    query = "INSERT IGNORE INTO ArticlesSentiment.Articles VALUES('{}','{}',{})".format(company, key,
                                                                                                        float(score))
                    cursor.execute(query)

        connection.commit()
        cursor.close()
        connection.close()

    def get_sentiments_for_company(self, company):

        self._create_database()
        self._create_table()

        connection = pymysql.connect(host='34.235.205.203',
                                     user='root',
                                     password='dwdstudent2015',
                                     db='ArticlesSentiment',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()

        stories = self.get_content(company=company)
        stories = dict(stories)

        for key in stories.keys():
            if key is not None:
                story = stories.get(key)
                score = self.__get_sentiment(story)
                query = "INSERT IGNORE INTO ArticlesSentiment.Articles VALUES('{}','{}',{})".format(company, key,
                                                                                                    float(score))
                cursor.execute(query)

        connection.commit()
        cursor.close()
        connection.close()


if __name__ == "__main__":
    spider = Spider()
    pprint(spider.get_sentiments())
