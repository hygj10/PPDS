import pymysql
from flask import Flask, jsonify, request

from sentiment_analysis import Spider

app = Flask(__name__)


def get_result_from_db(company_name):
    if isinstance(company_name, str):
        query = "SELECT * FROM ArticlesSentiment.Articles WHERE company = '{}';".format(company_name)
        print(query)

        connection = pymysql.connect(host='34.235.205.203',
                                     user='root',
                                     password='dwdstudent2015',
                                     db='ODIMatches',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()

        cursor.execute(query)

        results = cursor.fetchall()
        return results

    return None


@app.route('/api/company', methods=['GET'])
def get_scores():

    company_name = request.args.get("company_name", type=str)


    results = get_result_from_db(company_name)

    if len(results) == 0:
        print("Dynamic Fetching")
        spider = Spider()
        spider.get_sentiments_for_company(company_name)

    results = get_result_from_db(company_name)

    if results is None:
        return 400

    print(results)
    return jsonify(results), 200


if __name__ == "__main__":
    app.run(debug=True)
