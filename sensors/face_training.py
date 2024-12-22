import cv2
import numpy as np
from PIL import Image
import os


def main():
    # Path for face image database
    path = 'dataset'
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    print("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    faces, ids = getImagesAndLabels(path)
    recognizer.train(faces, np.array(ids))

    # Ensure the trainer directory exists
    output_dir = 'trainer'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save the model into trainer/trainer.yml
    recognizer.write(os.path.join(output_dir, 'trainer.yml')) 

    # Print the number of faces trained and end program
    print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))


def getImagesAndLabels(path):
    detector = cv2.CascadeClassifier('Cascades/haarcascade_frontalface_default.xml')
    if detector.empty():
        raise IOError("Haar cascade file not found or invalid path.")

    subfolders = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    faceSamples = []
    ids = []

    # Map folder names to integer IDs
    label_map = {os.path.basename(subfolder): idx for idx, subfolder in enumerate(subfolders, start=1)}

    for subfolder in subfolders:
        label_name = os.path.basename(subfolder)
        id = label_map[label_name]  # Get the integer ID for this folder

        imagePaths = [os.path.join(subfolder, f) for f in os.listdir(subfolder) if f.endswith(('.jpg', '.jpeg', '.png'))]

        for imagePath in imagePaths:
            try:
                PIL_img = Image.open(imagePath).convert('L')
                img_numpy = np.array(PIL_img, 'uint8')
                faces = detector.detectMultiScale(img_numpy)
                if len(faces) == 0:
                    print(f"[WARNING] No faces detected in image {imagePath}. Skipping.")
                    continue
                for (x, y, w, h) in faces:
                    faceSamples.append(img_numpy[y:y+h, x:x+w])
                    ids.append(id)
            except Exception as e:
                print(f"[ERROR] Skipping image {imagePath} due to error: {e}")

    return faceSamples, ids
    

if __name__ == '__main__':
    main()