from flask import Flask, render_template
import openai
import os

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html", user_name="Guest")


if __name__ == '__main__':
    app.run()
