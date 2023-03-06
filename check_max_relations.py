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

f = open("vg_150k_train.json")
examples = json.load(f)

max_relations = 0
for example in examples:
    walks = example["relations"]
    all_relations = [y for x in walks for y in x]
    all_relations = [rel for rel in all_relations if rel["relationship_id"] != -1]
    num_relations = len(all_relations)
    if num_relations > max_relations:
        max_relations = num_relations
print(max_relations)