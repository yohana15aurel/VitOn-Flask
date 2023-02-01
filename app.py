from flask import Flask,render_template,Response
import os

import cvzone
import cv2
from cvzone.PoseModule import PoseDetector
import math


# cap = cv2.VideoCapture(0)
detector = PoseDetector()

shirtFolderPath = "./Shirts"
listShirts = os.listdir(shirtFolderPath)
print(listShirts)

getimageShirt = cv2.imread(os.path.join(shirtFolderPath, listShirts[0]), cv2.IMREAD_UNCHANGED)
h, w, c = getimageShirt.shape

shirtRatioHeightWidth = h/w


pantFolderPath = "./Pants"
listPants = os.listdir(pantFolderPath)
print(listPants)

getimagePants = cv2.imread(os.path.join(pantFolderPath, listPants[0]), cv2.IMREAD_UNCHANGED)
h1, w1, c1 = getimagePants.shape

pantRatioHeightWidth = h1/w1

app=Flask(__name__)
camera=cv2.VideoCapture("./Videos/1.mp4")

def generate_frames():
    while True:
      
            
        ## read the camera frame
        success,frame=camera.read()
        if not success:
            break
        else:
            frame = detector.findPose(frame)
            lmList, bboxInfo = detector.findPosition(frame, bboxWithHands=False, draw=False)
            if lmList :
                # center = bboxInfo["center"]
                # cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)

                ##WIDTH OF KEYPOINT SHOULDER##
                x1, y1 = lmList[11][1:3]
                x2, y2 = lmList[12][1:3]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                length = math.hypot(x2-x1, y2-y1)

                ##WIDTH OF KEYPOINT WRIST##
                x1a, y1a = lmList[23][1:3]
                x2a, y2a = lmList[24][1:3]
         
                length2 = math.hypot(x2a-x1a, y2a-y1a)

             
                cv2.putText(frame, str(length2), (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255))


                ##SHIRT###
                lm11 = lmList[11][1:3]
                lm12 = lmList[12][1:3]
                

                ##PANTS
                lm23 = lmList[23][1:3]
                lm24 = lmList[24][1:3]

                imgShirt = cv2.imread(os.path.join(shirtFolderPath, listShirts[0]), cv2.IMREAD_UNCHANGED)

                fixedRatio = 300/length #widthOfShirt/widthOfKeyPoint

                widthOfShirt = int((lm11[0]-lm12[0])*fixedRatio)
            #  print(widthOfShirt)
                imgShirt = cv2.resize(imgShirt, (widthOfShirt,int(widthOfShirt*shirtRatioHeightWidth)))
                currentScale = (lm11[0]-lm12[0])/length
                offset = int(58*currentScale), int(54*currentScale)
                
                ###PANTS

                imgPants = cv2.imread(os.path.join(pantFolderPath, listPants[1]), cv2.IMREAD_UNCHANGED)


                fixedRatioPant = 320/192

                widthOfPant = int((lm23[0]-lm24[0])*fixedRatioPant)
                print(widthOfPant)
                # imgPants = cv2.resize(imgPants, (widthOfPant,int(widthOfPant*pantRatioHeightWidth)))
                imgPants = cv2.resize(imgPants, (widthOfPant,int(widthOfPant*pantRatioHeightWidth)))
                currentScale2 = (lm23[0]-lm24[0])/192
                offset2 = int(58*currentScale2), int(48*currentScale2)


                try:
                    frame = cvzone.overlayPNG(frame, imgPants, (lm24[0] - offset2[0], lm23[1] - offset2[1]))
                    frame = cvzone.overlayPNG(frame, imgShirt, (lm12[0] - offset[0], lm12[1] - offset[1]))
                

                
                except:
                    pass
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()

        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))

