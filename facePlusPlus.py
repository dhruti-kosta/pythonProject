#~/usr/bin/env python3
import requests
import pandas
import json
import webbrowser
import matplotlib
import matplotlib.pyplot as pyplot
import matplotlib.patches as patches 

# An object of Flask class is our WSGI application
## best practice says don't use commas in imports
# use a single line for each import
from flask import Flask
from flask import redirect
from flask import url_for
from flask import request
from flask import render_template, make_response

# Flask constructor takes the name of current
# module (__name__) as argument
app = Flask(__name__)

# GLOBAL
API = "https://api-us.faceplusplus.com/facepp/v3/detect?"

@app.route("/") # user can land at "/"
def start():
    return render_template("index.html") # look for index.html

## This is where we want to redirect users to
# @app.route("/success/<image_url>")
# def success(image_url):
#     api_key = "api_key=iCqtqdYpKctOL_AIllv45VYl2bMYUPre"
#     api_secret = "api_secret=zmpiNh3fu67LXAiWqWhWUCMhJDG3Xabk"
#     img_url = image_url
#     return_landmark = "return_landmark=1"
#     return_attributes = "return_attributes=gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,ethnicity,beauty,mouthstatus,eyegaze,skinstatus"

#     finalAPI = API + api_key + "&" + api_secret + "&" + img_url
#     # call the webservice with our key
#     res = requests.post(finalAPI)
#     #return res.json()
#     return render_template("facedetection.html", renderjson = res.json()) # look for facedetection.html

    #itemsdf = pandas.DataFrame(res.json())
    #itemsdf.to_json("faces.json")

    # facedata = res.json()["faces"]
    # print(f"No of Faces in this photograph: {len(facedata)}")

@app.route("/index", methods = ["POST", "GET"])
def index():
    if request.method == "POST":
        if request.form.get("imageurl"): # if imageurl was assigned via the POST
            imageurl = request.form.get("imageurl") # grab the value of imageurl from the POST
        else: # if a user sent a post without imageurl then assign value defaulturl
            imageurl = "https://www.rollingstone.com/wp-content/uploads/2019/09/FriendsLead.jpg"
    # GET would likely come from a user interaacting with a browser
    elif request.method == "GET":
        if request.args.get("imageurl"): # if imageurl was assigned as a parameter=value
            imageurl = request.args.get("imageurl") # pull imageurl from localhost:5000/facedetect?imageurl=<defaulturl>
        else: # if imageurl was not passed...
            imageurl = "https://www.rollingstone.com/wp-content/uploads/2019/09/FriendsLead.jpg" # ...then url is just defaulturl
    
    api_key = "api_key=iCqtqdYpKctOL_AIllv45VYl2bMYUPre"
    api_secret = "api_secret=zmpiNh3fu67LXAiWqWhWUCMhJDG3Xabk"
    img_url = "image_url=" + imageurl
    return_landmark = "return_landmark=1"
    return_attributes = "return_attributes=gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,ethnicity,beauty,mouthstatus,eyegaze,skinstatus"

    finalAPI = API + api_key + "&" + api_secret + "&" + img_url + "&" + return_landmark + "&" + return_attributes 
    # call the webservice with our key
    res = requests.post(finalAPI)
    #print(res.json())

    # Download the image
    with open("user.jpeg", 'wb') as handle:
        image_response = requests.get(imageurl, stream=True)

    # Display rectagles on each faces found on image entered
    response = res.json()
    for face in response.get("faces"):
        face_rectangle = face.get("face_rectangle")
        img = matplotlib.image.imread("user.jpeg")
        ax = pyplot.subplots(1)
        rect = patches.Rectangle((face_rectangle.get("left"),face_rectangle.get("top")),face_rectangle.get("width"),face_rectangle.get("height"), edgecolor='r', facecolor="none")
        #ax.imshow(img) #Displays an image
        #ax.add_patch(rect) #Add rectangle to image
        

    return render_template("facedetection.html", returnjson = res.json()) # look for facedetection.html

if __name__ == "__main__":
    port = 5000
    url = "http://127.0.0.1:{0}".format(port)
    webbrowser.open(url)
    app.run(port=port, debug=False)