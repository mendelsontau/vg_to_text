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
from tqdm import tqdm

f = open("vg_new_improved_text_dataset.json")
examples = json.load(f)
print(len(examples))
fixed_examples = []
for sample in tqdm(examples):
    crop_dimensions = sample["to_crop"]
    min_x = crop_dimensions[0]
    min_y = crop_dimensions[1]
    max_x = crop_dimensions[2]
    max_y = crop_dimensions[3]
    image_h = max_y - min_y
    image_w = max_x - min_x

    all_objects_dict = sample["objects"]
    objects = []
    for id in all_objects_dict:
        objects.append(all_objects_dict[id])

    walks = sample["relations"]
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
    check = (bounding_boxes_x0_y0_x1_y1[:, 2:] >= bounding_boxes_x0_y0_x1_y1[:, :2].all())
    if check.all().item():
        fixed_examples.append(sample) 
print(len(fixed_examples))
random.shuffle(fixed_examples)

val_examples = fixed_examples[:16]
train_examples = fixed_examples[16:16 + 150000]
out_file = open("vg_150k_val.json", "w") 
json.dump(val_examples, out_file, indent = 6)
out_file.close()
out_file = open("vg_150k_train.json", "w") 
json.dump(train_examples, out_file, indent = 6)
out_file.close()