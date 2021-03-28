from flask import Flask
import os
print(os.environ['RDS_HOSTNAME'])

application = Flask(__name__)

@application.route("/")
def test():
    return ("It works!"+(os.environ['RDS_HOSTNAME']))

