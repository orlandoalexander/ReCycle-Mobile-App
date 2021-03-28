from flask import Flask

application = Flask(__name__)

@application.route("/")
def test():
    return "It works!"

