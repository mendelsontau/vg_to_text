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

f = open("vg_new_improved_text_dataset.json")
examples = json.load(f)

random.shuffle(examples)
val_examples = examples[:16]
train_examples = examples[16:16 + 100000]
out_file = open("vg_100k_val.json", "w") 
json.dump(val_examples, out_file, indent = 6)
out_file.close()
out_file = open("vg_100k_train.json", "w") 
json.dump(train_examples, out_file, indent = 6)
out_file.close()
