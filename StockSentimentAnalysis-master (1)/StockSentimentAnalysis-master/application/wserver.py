from flask import Flask, render_template
import MySQLdb as mdb

app = Flask(__name__)

@app.route('/stocks')
def articles():

    con = mdb.connect(host = '34.235.205.203', 
                          user = 'root',
                          password = 'dwdstudent2015',
                          db = 'ArticlesSentiment', 
                          charset='utf8', 
                          use_unicode=True);

    cur = con.cursor(mdb.cursors.DictCursor)
    cur.execute("SELECT company, article_url, score FROM Articles")
    article = cur.fetchall()
    cur.close()
    con.close()

    return render_template('index.html', articles=article)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)