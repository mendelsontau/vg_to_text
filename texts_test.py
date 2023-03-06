import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import torch
import torchvision
from PIL import Image
import re
import torchvision.transforms as transforms
import torchvision
from torchvision.transforms import InterpolationMode
import numpy as np
import random
# Import the image editing libraries from PIL
from PIL import Image, ImageDraw, ImageFont, ImageOps

def repair_text(text):
    text_arr = text.split()
    new_text_arr = []
    for i in range(len(text_arr) - 1):
        if text_arr[i] != text_arr[i+1]:
            new_text_arr.append(text_arr[i])
    new_text_arr.append(text_arr[-1])
    new_text = " ".join(new_text_arr)
    return new_text


def create_text_from_graph(walks, all_objects_dict):
    text = ""
    for relations in walks:
        r = relations[0]
        if r["object_id"] == -1:
            if "attributes" in all_objects_dict[str(r["subject_id"])]:
                text += all_objects_dict[str(r["subject_id"])]["attributes"][0] + " " + all_objects_dict[str(r["subject_id"])]["names"][0]
            else:
                text += all_objects_dict[str(r["subject_id"])]["names"][0]
        else:               
            if "attributes" in all_objects_dict[str(r["subject_id"])]:
                text += all_objects_dict[str(r["subject_id"])]["attributes"][0] + " " + all_objects_dict[str(r["subject_id"])]["names"][0] + " " + r["predicate"] + " "
            else:
                text += all_objects_dict[str(r["subject_id"])]["names"][0] + " " + r["predicate"] + " "
            if len(relations) != 1:
                for i in range (1, len(relations)):
                    r = relations[i]
                    if "attributes" in all_objects_dict[str(r["subject_id"])]:
                        text += all_objects_dict[str(r["subject_id"])]["attributes"][0] + " " + all_objects_dict[str(r["subject_id"])]["names"][0] + " " + r["predicate"] + " "
                    else:
                        text += all_objects_dict[str(r["subject_id"])]["names"][0] + " " + r["predicate"] + " "
            r = relations[-1]
            if "attributes" in all_objects_dict[str(r["object_id"])]:
                text += all_objects_dict[str(r["object_id"])]["attributes"][0] + " " + all_objects_dict[str(r["object_id"])]["names"][0]
            else:
                text += all_objects_dict[str(r["object_id"])]["names"][0]
        text += ". "
    return text

split = "val"
f = open(os.path.join("vg_150k_val.json"))
data = json.load(f)
transform = transforms.Compose([
    transforms.PILToTensor()
])
resize = transforms.Resize((512,512), interpolation=InterpolationMode.BICUBIC)
for ss in range (len(data)):
    idx  = ss
    bad = []
    print(ss)
    #load image
    image_url = data[idx]["image_data"]["url"]
    crop_dimensions = data[idx]["to_crop"]
    min_x = crop_dimensions[0]
    min_y = crop_dimensions[1]
    max_x = crop_dimensions[2]
    max_y = crop_dimensions[3]
    image_h = max_y - min_y
    image_w = max_x - min_x
    url_parts = image_url.split("/")
    folder = url_parts[5]
    filename = url_parts[6]
    image_path = os.path.join(folder,folder,filename)

    image = Image.open(image_path)
    image = image.crop(crop_dimensions)


    all_objects_dict = data[idx]["objects"]
    objects = []
    for id in all_objects_dict:
        objects.append(all_objects_dict[id])

    walks = data[idx]["relations"]
    text = create_text_from_graph(walks, all_objects_dict)



    #prepare bounding boxes
    objects_bbs = [[ob["x"],ob["y"],ob["w"], ob["h"]] for ob in objects]
    for obj in objects_bbs:
        new_x1 = obj[0]
        new_y1 = obj[1]
        new_x2 = obj[0] + obj[2]
        new_y2 = obj[1] + obj[3]
        if obj[0] < min_x:
            new_x1 = min_x
        if obj[1] < min_y:
            new_y1 = min_y
        if obj[0] + obj[2] > max_x:
            new_x2 = max_x
        if obj[1] + obj[3] > max_y:
            new_y2 = max_y
        obj[0] = new_x1 - min_x
        obj[1] = new_y1 - min_y
        obj[2] = new_x2 - new_x1
        obj[3] = new_y2 - new_y1
    bounding_boxes = [[(ob[0] + 0.5*ob[2])/image_w,(ob[1] + 0.5*ob[3])/image_h,min((ob[2])/image_w,1.0),min((ob[3])/image_h,1.0)] for ob in objects_bbs]
    bounding_boxes_x0_y0_x1_y1 = torch.tensor([[ob[0] - 0.5*ob[2],ob[1] - 0.5*ob[3],ob[0] + 0.5*ob[2],ob[1] + 0.5*ob[3]] for ob in bounding_boxes])   
    bounding_boxes1 = [[(ob[0] + 0.5*ob[2])/image_w,(ob[1] + 0.5*ob[3])/image_h,min((ob[2])/image_w,1.0),min((ob[3])/image_h,1.0)] for ob in objects_bbs]
    bounding_boxes3 = torch.tensor([[ob[0] - 0.5*ob[2],ob[1] - 0.5*ob[3],ob[0] + 0.5*ob[2],ob[1] + 0.5*ob[3]] for ob in bounding_boxes1])*512
    bounding_boxes2 = torch.tensor([[ob[0],ob[1],ob[0] + ob[2],ob[1] + ob[3]] for ob in objects_bbs])
    image = resize(image)
    img_tensor  = transform(image)


    #prepare object descriptions
    object_descriptions = [obj["attributes"][0] + " " + obj["names"][0] if "attributes" in obj else obj["names"][0] for obj in objects]
    object_descriptions = [repair_text(desc)for desc in object_descriptions]
    image_w_bb = torchvision.utils.draw_bounding_boxes(img_tensor, bounding_boxes3, labels=object_descriptions, colors="black")
    new_image = transforms.ToPILImage()(image_w_bb)
    new_image.save("examples/img_bb_" + str(idx) + ".jpg")
    print(object_descriptions)
    print(text)
