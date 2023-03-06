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


# f = open("attributes.json")
# attributes = json.load(f)
# attributes_counter = {}
# for img in attributes:
#     for a in img["attributes"]:
#         if "attributes" in a:
#             img_attributes = a["attributes"]
#             for att in img_attributes:
#                 att = att.strip().lower()
#                 if att in attributes_counter:
#                     attributes_counter[att] += 1
#                 else:
#                     attributes_counter[att] = 1
# sorted_att_counter = sorted(attributes_counter.items(), key=lambda x:x[1])
# relevant_attributes = sorted_att_counter[-300:]
# attributes_annotations = {}
# atts_in_cat = {}
# atts_in_cat["size"] = []
# atts_in_cat["material"] = []
# atts_in_cat["color"] = []
# atts_in_cat["location"] = []
# atts_in_cat["state"] = []
# atts_in_cat["action"] = []
# atts_in_cat["shape"] = []

# for att in relevant_attributes:
#     att_name = att[0]
#     if att_name in attributes_annotations:
#         continue
#     print("keep " + att_name + " in attributes?")
#     answer = str(input())
#     if answer == "n":
#         continue
#     else:
#         att_dict = {}
#         print("state the category for " + att_name)
#         answer = str(input())
#         att_dict["category"] = answer
#         attributes_annotations[att_name] = att_dict
#         atts_in_cat[answer].append(att_name)

# out_file = open("attributes_annotations.json", "w") 
# json.dump(attributes_annotations, out_file, indent = 6)
# out_file.close()

# out_file = open("atts_in_cat.json", "w") 
# json.dump(atts_in_cat, out_file, indent = 6)
# out_file.close()

f = open("attributes_annotations.json")
attributes_annotations = json.load(f)
f = open("atts_in_cat.json")
atts_in_cat = json.load(f)

for att_name in attributes_annotations:
    if attributes_annotations[att_name]["category"] == "state" or attributes_annotations[att_name]["category"] == "action":
        continue
    if "negations" in attributes_annotations[att_name]:
        continue
    print("the attribute " + att_name +  " is from category " + attributes_annotations[att_name]["category"])
    print("which of the following is not a negation of " + att_name + "?")
    print(atts_in_cat[attributes_annotations[att_name]["category"]])
    atts_in_category = atts_in_cat[attributes_annotations[att_name]["category"]].copy()
    answer = str(input())
    if answer == "remove":
       attributes_annotations[att_name]["negations"] = []
       continue
    if answer != "":
        answer = answer.split(",")
        for a in answer:
            atts_in_category.remove(a)
    atts_in_category.remove(att_name)
    attributes_annotations[att_name]["negations"] = atts_in_category
    out_file = open("attributes_annotations.json", "w") 
    json.dump(attributes_annotations, out_file, indent = 6)
    out_file.close()



