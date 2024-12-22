import cv2
import os

def main():
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) # set video width
    cam.set(4, 480) # set video height
    
    faceCascade = cv2.CascadeClassifier('Cascades/haarcascade_frontalface_default.xml')

    face_id = input('\n enter user id end press <return> ==>  ')
    print("\n [INFO] Initializing face capture. Look the camera and wait ...")

    count = 0
    while(True):
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        faces = faceCascade.detectMultiScale(
            gray,
            #image size is reduced at each image scale
            scaleFactor=1.2,
            minNeighbors=5,
            #minSize is the minimum rectangle size to be considered a face.
            minSize=(20,20)
        )

        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w, y+h), (255, 0, 0), 2)
            count += 1
            roi_gray = gray[y:y+h, x:x+w]
            roi_gray = img[y:y+h, x:x+w]

        cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
        cv2.imshow('image', img)
        # cv2.imshow('gray', gray)
        
        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break
        elif count >= 30: # Take 30 face sample and stop video
            break

    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()