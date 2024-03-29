__copyright__   = "Copyright 2024, VISA Lab"
__license__     = "MIT"

import os
import imutils
import cv2
import json
from PIL import Image, ImageDraw, ImageFont
from facenet_pytorch import MTCNN, InceptionResnetV1
from shutil import rmtree
import numpy as np
import torch


mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embeding conversion

def face_recognition_function(folder_name):
    if not os.path.exists(folder_name):
        print(f"Folder {folder_name} does not exist!")
        return None
    name = ""
    pics = sorted(os.listdir(folder_name))
    return_names = dict()
    for pic in pics:
        path = os.path.join(folder_name, pic)
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        face,prob = mtcnn(img, return_prob=True, save_path=None)
        saved_data = torch.load('/tmp/data.pt')  # loading data.pt file
        if face != None:
            emb = resnet(face.unsqueeze(0)).detach()  # detech is to make required gradient false
            embedding_list = saved_data[0]  # getting embedding data
            name_list = saved_data[1]  # getting list of names
            dist_list = []  # list of matched distances, minimum distance is used to identify the person
            for idx, emb_db in enumerate(embedding_list):
                dist = torch.dist(emb, emb_db).item()
                dist_list.append(dist)
            idx_min = dist_list.index(min(dist_list))
            pic_extension = pic.split(".")[0]
            return_names[pic_extension] = name_list[idx_min]
    return return_names


