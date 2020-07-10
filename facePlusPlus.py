#~/usr/bin/env python3
import requests
import json
import webbrowser
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import os
import ast

# An object of Flask class is our WSGI application
## best practice says don't use commas in imports
# use a single line for each import
from flask import Flask
from flask import request
from flask import render_template

# Flask constructor takes the name of current
# module (__name__) as argument
app = Flask(__name__)

# GLOBAL
API = "https://api-us.faceplusplus.com/facepp/v3/detect?"

@app.route("/") # user can land at "/"
def start():
    return render_template("index.html") # look for index.html

@app.route("/index", methods = ["POST", "GET"])
def index():
    if request.method == "POST":
        if request.form.get("imageurl"): # if imageurl was assigned via the POST
            imageurl = request.form.get("imageurl") # grab the value of imageurl from the POST
        else: # if a user sent a post without imageurl then assign value defaulturl
            imageurl = "https://www.rollingstone.com/wp-content/uploads/2019/09/FriendsLead.jpg"
    
    # Download the image
    img_data = requests.get(imageurl).content
    with open('static/images/source_image.jpg', 'wb') as handler:
        handler.write(img_data)

    # Resize source image and save it
    source_img = Image.open("static/images/source_image.jpg")
    basewidth = 550
    wpercent = (basewidth/float(source_img.size[0]))
    hsize = int((float(source_img.size[1])*float(wpercent)))
    source_img = source_img.resize((basewidth,hsize), Image.ANTIALIAS)
    source_img.save("static/images/main_image.jpg", "JPEG")

    #Get all necessory details to call API
    api_key = "api_key=iCqtqdYpKctOL_AIllv45VYl2bMYUPre"
    api_secret = "api_secret=zmpiNh3fu67LXAiWqWhWUCMhJDG3Xabk"
    #img_url = "image_url=" + imageurl
    return_landmark = "return_landmark=1"
    return_attributes = "return_attributes=gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,ethnicity,beauty,mouthstatus,eyegaze,skinstatus"
    files = {'image_file': open('static/images/main_image.jpg', 'rb')}
    
    # call the Face++ API to get data
    finalAPI = API + api_key + "&" + api_secret + "&" + return_landmark + "&" + return_attributes 
    res = requests.post(finalAPI,files=files)
    facedata = res.json().get("faces")

    #Remove cropped images
    for filename in os.listdir('static/images/cropfaces'):
        if filename.endswith('.jpg'):
            os.remove('static/images/cropfaces/' + filename) 
    #Remove points cropped images
    for filename in os.listdir('static/images/pointfaces'):
        if filename.endswith('.jpg'):
            os.remove('static/images/pointfaces/' + filename) 

    # Draw rectangles on each face and save new image
    main_image = Image.open("static/images/main_image.jpg")
    mainimage = Image.open("static/images/main_image.jpg")
    count = 1
    faceslist = {} # to send all faces and attributes
    for face in facedata: 
        face_rectangle = face.get("face_rectangle")
        x = face_rectangle.get("left")
        y = face_rectangle.get("top")
        w = face_rectangle.get("width")
        h = face_rectangle.get("height")
        
        # create cropped images of each faces and save in cropfaces folder
        im_crop = main_image.crop((x, y, (x + w), (y + h)))
        im_crop.save('static/images/cropfaces/' + str(count) + '.jpg', "JPEG")

        

        # add points to cropped face images and save them in pointfaces folder
        face_landmark = face.get("landmark")
        im_landmark = ImageDraw.Draw(mainimage)
        for mark in face_landmark:
            im_landmark.point((face_landmark.get(mark).get("x"), face_landmark.get(mark).get("y")),fill="Blue")
        
        # save landmark pointed face image after crop
        im_crop = mainimage.crop((x, y, (x + w), (y + h)))
        im_crop = im_crop.resize((150,150), Image.ANTIALIAS)
        im_crop.save('static/images/pointfaces/' + str(count) + '.jpg', "JPEG", quality=100)

        #Draw rectangles on main image
        draw = ImageDraw.Draw(main_image)
        draw.rectangle([(x,y),(x + w,y + h)], outline=(0, 0, 255), width=2)
        
        # Face attributes to show when click on perticular face
        attributes = face.get("attributes")
        age = attributes.get("age").get("value")
        gender = attributes.get("gender").get("value")
        smile_value = attributes.get("smile").get("value")
        smile_threshold = attributes.get("smile").get("threshold")

        eye_status = ""
        status = 0

        left_eye = attributes.get("eyestatus").get("left_eye_status")
        for lefteye in left_eye:
            if(status == 0):
                status = left_eye.get(lefteye)
                eye_status = next(key for key, value in left_eye.items() if value == status)
            else:
                if(status < left_eye.get(lefteye)):
                    status = left_eye.get(lefteye)
                    eye_status = next(key for key, value in left_eye.items() if value == status)
        left_eye_status = getEyeStatus(eye_status)

        right_eye = attributes.get("eyestatus").get("right_eye_status")
        for righteye in right_eye:
            if(status == 0):
                status = right_eye.get(righteye)
                eye_status = next(key for key, value in right_eye.items() if value == status)
            else:
                if(status < right_eye.get(righteye)):
                    status = right_eye.get(righteye)
                    eye_status = next(key for key, value in right_eye.items() if value == status)
        right_eye_status = getEyeStatus(eye_status)

        # dictionary to send data to display details on face details page
        attributesDict = {}
        attributesDict["age"] = age
        attributesDict["gender"] = gender
        attributesDict["smile"] = "value: " + str(smile_value) + "; threshold: " + str(smile_threshold)
        attributesDict["lefteyestatus"] = left_eye_status
        attributesDict["righteyestatus"] = right_eye_status
        
        facedict = {}
        facedict["filename"] = str(count) + '.jpg'
        facedict["attributes"] = attributesDict
        faceslist[count] = facedict

        count += 1

    # save rectangle faced image
    main_image.save("static/images/facedetection_image.jpg", "JPEG")
    
    # render facedetection.html for display new image
    return render_template("facedetection.html", returnimage = "facedetection_image.jpg", lsfaces = faceslist, lenfaces = (count -1)) # look for facedetection.html

@app.route("/faces", methods = ["POST", "GET"])
def faces():
    #get all crop images
    if request.method == "GET":
        if request.args.get("lsfaces"): 
            lsfaces = ast.literal_eval(request.args.get("lsfaces")) 
        if request.args.get("lenfaces"): 
            lenfaces = request.args.get("lenfaces") 

    return render_template("faces.html", returnimage = "facedetection_image.jpg", lsfaces = lsfaces, lenfaces = lenfaces) # look for faces.html

@app.route("/facedetails", methods = ["POST", "GET"])
def facedetails():
    #get details of selected face
    lsfaces = {}
    if request.method == "GET":
        if request.args.get("lsfaces"): 
            lsfaces = ast.literal_eval(request.args.get("lsfaces")) 
        if request.args.get("lenfaces"): 
            lenfaces = request.args.get("lenfaces") 
        if request.args.get("filename"): 
            filename = request.args.get("filename")

    lsfacedetails = {}
    if filename != '':
        for key,value in lsfaces.items():
            for key1,value1 in value.items():
                if key1 == 'filename':
                    if(filename == value1):
                        lsfacedetails = lsfaces['attributes']
                        break

    return render_template("facedetails.html", lsfaces = lsfacedetails, lenfaces = lenfaces) # look for facedetection.html

def getEyeStatus(eyestatus):
    switcher={
        'no_glass_eye_open':  "No Glass, Open",
        'no_glass_eye_close':  "No Glass, Close",
        'normal_glass_eye_open':  "Glass, Open",
        'normal_glass_eye_close':  "Glass, close",
        'dark_glasses':  "Dark Glasses",
        'occlusion':  "occlusion",
    }
    return switcher.get(eyestatus,"Invalid day of week")

if __name__ == "__main__":
    port = 5000
    url = "http://127.0.0.1:{0}".format(port)
    webbrowser.open(url)
    app.run(port=port, debug=True)