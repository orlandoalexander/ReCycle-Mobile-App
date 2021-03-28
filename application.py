from flask import Flask

appplication = Flask(__name__)

@appplication.route("/")
def test():
    return "It works!"

