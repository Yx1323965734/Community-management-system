from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'hello world!'

@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/static')
def static_demo():
    return render_template("static.html")

@app.route('/notice')
def notice():
    return render_template("notice.html")

if __name__ == '__main__':
    app.run()