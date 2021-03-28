from flask import Flask, request #flask is used for developing web applications
from flask_restful import Api, Resource

appplication = Flask(__name__)
api = Api(appplication) #wrap app in restful Api

@appplication.route("/test")
def test():
    return "It works!"

class returnNouns(Resource): #class that is a resource - for GET, PUT and DELETE requests
    def get(self): #function which is run when get request is made to the URL
        return ("hi") #201 is message to say data created


api.add_resource(returnNouns, "/nouns") #adds the class 'returnNouns' to the Api as the class is a resource. This resource is found by making a GET request to the URL followed by "/nouns"

if __name__ == "__main__":
    appplication.run(debug=True) #begins running the Api server