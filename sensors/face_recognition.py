import cv2
import numpy as np
import os
import time

def get_folder_mapping(dataset_path):
    """Create a mapping of IDs to folder names."""
    id_to_folder = {}
    try:
        folders = os.listdir(dataset_path)
        for folder in folders:
            if folder.isdigit():  # Ensure the folder name is a number
                id_to_folder[int(folder)] = folder
    except Exception as e:
        print(f"[ERROR] Unable to map dataset folders: {e}")
    return id_to_folder


def face_recognition():
    # Step 2: Load the trained model
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')
    cascadePath = "Cascades/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)
    font = cv2.FONT_HERSHEY_SIMPLEX

    dataset_path = "./dataset"
    id_to_folder = get_folder_mapping(dataset_path)

    cam = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cam.isOpened():
        print("[ERROR] Camera not accessible.")
        return None

    cam.set(3, 640)  # set video width
    cam.set(4, 480)  # set video height

    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    fail_count = 0
    start_time = time.time()

    while fail_count < 10:

        elapsed_time = time.time() - start_time
        if elapsed_time > 30:
            print("[INFO] Timeout reached. Exiting face recognition.")
            return None


        ret, img = cam.read()
        if not ret:
            print("[ERROR] Failed to grab frame from camera.")
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

            if 30 < confidence < 100:  # Face recognized with confidence
                folder_name = id_to_folder.get(id, "Unknown")
                confidence_text = f"{round(100 - confidence)}%"
                print(f"Face matched for folder '{folder_name}' with confidence of {confidence_text}")
                res = {"id": id, "folder_name": folder_name, "confidence": confidence_text}
                cam.release()
                cv2.destroyAllWindows()
                return res
            else:
                fail_count += 1
                print(f"Unknown Face. Confidence {round(100 - confidence)}%. Attempt {fail_count}")

    cam.release()
    cv2.destroyAllWindows()
    return None


if __name__ == "__main__":
    result = face_recognition()
    if result:
        print(f"Recognized ID: {result['id']}, Folder: {result['folder_name']}, Confidence: {result['confidence']}")
    else:
        print("Face recognition failed.")
