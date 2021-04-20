from flask import Flask, request #flask is used for developing web applications
from flask_restful import Api, Resource, reqparse
import mysql.connector
import requests

application = Flask(__name__)
api = Api(application) #wrap app in restful Api

host = "aa1vi5r7zrnde8p.cnem9ngqo5zs.eu-west-2.rds.amazonaws.com"
user = "orlandoalexander"
passwd = "RecycleApp"

mydb = mysql.connector.connect(host=host, user=user, passwd=passwd, database="ebdb")  # initialises the database
mycursor = mydb.cursor()  # initialises a cursor which allows you to communicate with mydb (MySQL database)


@application.route("/")
def test():
    return "Working"

class returnRecyclingInfo(Resource): #class that is a resource - for GET, PUT and DELETE requests
    def post(self): #function which is run when get request is made to the URL
        self.nouns = []
        self.input = list((request.form["input"]).split(" ")) #self.input = request.form["input"] # data is in JSON format. JSON file format is essentially a Python dictionary. The returned format must be 'JSON serializable' (i.e. in a valid JSON format - a dictionary)
        self.county = request.form["county"]
        for word in self.input:
            query = ("SELECT * FROM Nouns WHERE Noun ='%s'" % (word))
            mycursor.execute(query) # returns all the values in the column 'noun' that match i.
            if len(mycursor.fetchall()) > 0:  # if the MySQL execution returns a value, the word is a noun and so is added to the keywords list.
                synonym_list = self.synonym_finder(word)
                for synonym in synonym_list:
                    self.nouns.extend(synonym)
            else:
                pass
        return self.get_category()

    def synonym_finder(self, word):
        self.synonym_list = []
        app_id = "b604d757"
        app_key = "09b4bee1fe710211531296ff8ec734f3"
        language = "en-gb"
        url = "https://od-api.oxforddictionaries.com:443/api/v2/thesaurus/" + language + "/" + word.lower()  # url reuquest to the api
        r = requests.get(url, headers={"app_id": app_id, "app_key": app_key})
        if r.status_code == 200:  # error checking - if no results returned by the thesaurus, an error message won't be thrown
            num_synonyms = len(r.json()["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0][
                                   "synonyms"])  # number of synonyms returned by the API
            for synonym in range(0, num_synonyms):
                self.synonym_list.append(
                    r.json()["results"][0]["lexicalEntries"][0]["entries"][0]["senses"][0]["synonyms"][synonym][
                        "text"])  # prints the synonyms returned by the api
        else:
            pass
        return (self.synonym_list)

    def get_category(self):
        for key in self.nouns:
            print(key)
            mycursor.execute("SELECT * FROM Categories WHERE `County` = '%s' AND `Type-main` = '%s' LIMIT 1" % ("Dacorum", key.capitalize()))  # executes query to find the main category type of the user's item. Limit 1 ensures that the results do not flow into the next execution of the db cursor, which would cause an Unread Result Found error
            if mycursor.fetchone() != None:  # if the query returns a result, this result will be stored in the variable 'self.item_type'
                #return key
                self.nouns.remove(key)
                self.itemMainType = key
                for key in self.nouns:
                    mycursor.execute(
                        "SELECT * FROM Categories WHERE `County` = '%s' AND `Type-main` = '%s' AND `Type-sub` = '%s' LIMIT 1" % (
                        "Dacorum", self.itemMainType.capitalize(), key.capitalize()))
                    result1 = mycursor.fetchone()
                    if result1 != None:
                        mycursor.execute("SELECT * FROM ExtraInfo WHERE `County/Type` = '%s' LIMIT 1" % ("Dacorum/Bottle"))
                        result2 = mycursor.fetchone()
                        print(result2)
                        if result1[3] == "Y":
                            self.reyclable = True
                            if result2 != None:
                                self.extraInfo = result2[2]
                        else:
                            self.recyclable = False
                            if result2 != None:
                                self.extraInfo = result2[1]
        return self.extraInfo
        




api.add_resource(returnRecyclingInfo, "/ReyclingInfo") #adds the class 'returnNouns' to the Api as the class is a resource. This resource is found by making a GET request to the URL followed by "/nouns"

if __name__ == "__main__":
    application.run(debug=True) #begins running the Api server
