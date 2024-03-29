__copyright__   = "Copyright 2024, VISA Lab"
__license__     = "MIT"

import os
import imutils
import cv2
import json
from PIL import Image
from facenet_pytorch import MTCNN
from shutil import rmtree

mtcnn = MTCNN(keep_all=True, device='cpu')
               
def face_extraction_function(folder_name):
    if not os.path.exists(folder_name):
        print(f"Folder {folder_name} does not exist!")
        return None

    pics = sorted(os.listdir(folder_name))
    for pic in pics:
        path = os.path.join(folder_name, pic)
        frame = cv2.imread(path, cv2.IMREAD_COLOR)
        boxes, _ = mtcnn.detect(frame)

        if boxes is None:
            rmtree(folder_name)
            return

        for box in boxes:
            cv2.rectangle(frame,
                          (int(box[0]), int(box[1])),
                          (int(box[2]), int(box[3])),
                          (0, 255, 0),
                          2)
            cv2.imwrite(path,frame)
    return folder_name

