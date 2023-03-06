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


f = open("relations_transitivity.json")
relationships = json.load(f)
relations_annotations = {}
for rel in relationships:
    rel_dict = {}
    rel_dict["symmetry"] = relationships[rel]
    print("type negations for the relationship " + rel)
    answer = str(input())
    answer.split(",")
    rel_dict["negations"] = answer
    relations_annotations[rel] = rel_dict

out_file = open("relations_annotations.json", "w") 
json.dump(relations_annotations, out_file, indent = 6)
out_file.close()
