from flask import Flask, request #flask is used for developing web applications
from flask_restful import Api, Resource, reqparse
import mysql.connector

application = Flask(__name__)
api = Api(application) #wrap app in restful Api

host = "aaq2ah44zclim.cnem9ngqo5zs.eu-west-2.rds.amazonaws.com"
user = "orlandoalexander"
passwd = "B3rkham5t3d"

mydb = mysql.connector.connect(host=host, user=user, passwd=passwd, database="ebdb")  # initialises the database
mycursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)


@application.route("/")
def test():
    return "Working"

class returnNouns(Resource): #class that is a resource - for GET, PUT and DELETE requests
    def post(self): #function which is run when get request is made to the URL
        self.output = []
        self.input = list((request.form["input"]).split(" ")) #self.input = request.form["input"] # data is in JSON format. JSON file format is essentially a Python dictionary. The returned format must be 'JSON serializable' (i.e. in a valid JSON format - a dictionary)
        for i in self.input:
            query = ("SELECT * FROM Nouns WHERE noun='%s'" % (i))
            mycursor.execute(query) # returns all the values in the column 'noun' that match i.
            if len(mycursor.fetchall()) > 0:  # if the MySQL execution returns a value, the word is a noun and so is added to the keywords list.
                self.output.append(i.capitalize())
        self.output = ", ".join(self.output)
        return self.output


api.add_resource(returnNouns, "/nouns") #adds the class 'returnNouns' to the Api as the class is a resource. This resource is found by making a GET request to the URL followed by "/nouns"

if __name__ == "__main__":
    application.run(debug=True) #begins running the Api server
