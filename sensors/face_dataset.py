import cv2
import os
from face_training import main as train_model  # Import the training script

def face_dataset(employee_id):
    cam = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cam.set(3, 640) # set video width
    cam.set(4, 480) # set video height
    
    faceCascade = cv2.CascadeClassifier('Cascades/haarcascade_frontalface_default.xml')

    face_id = employee_id
    print("\n [INFO] Initializing face capture. Look the camera and wait ...")

    if not cam.isOpened():
        print("[ERROR] Camera not accessible.")
        return None

    count = 0
    while(True):
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        if not ret:
            print("[ERROR] Failed to grab a frame from the camera.")
            break

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

        save_path = f"dataset/{str(face_id)}"
        os.makedirs(save_path, exist_ok=True)
        cv2.imwrite(f"{save_path}/User_{str(face_id)}_{str(count)}.jpg", gray[y:y+h, x:x+w])

        print(f"Img {count} Saved")
        # cv2.imshow('gray', gray)
        
        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break
        elif count >= 50: # Take 30 face sample and stop video
            break

    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()
    
    # Step 1: Train the model before recognizing faces
    print("\n[INFO] Updating the trainer.yml file...")
    train_model()  # Calls the training script to update `trainer.yml`

# if __name__ == '__main__':
#     main()