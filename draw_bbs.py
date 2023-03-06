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


transform = transforms.Compose([
    transforms.PILToTensor()
])
resize = transforms.Resize((224,224), interpolation=InterpolationMode.BICUBIC)
f = open("objects.json")
objects = json.load(f)
f = open("image_data.json")
image_data = json.load(f)
i = 5
image_objects = objects[1]
im_data = image_data[1]
image_url = im_data["url"]
url_parts = re.split("/|//", image_url)
fixed_url = os.path.join(url_parts[5],url_parts[5],url_parts[6])
image = Image.open(fixed_url)
image = resize(image)
img_tensor  = transform(image)
ten_objects = [image_objects["objects"][i] for i in[5,7,9,11,12]]
boxes = [[ob["x"]/im_data["width"]*224,ob["y"]/im_data["height"]*224,min(ob["x"] + ob["w"], im_data["width"] - 1)/im_data["width"]*224, min(ob["y"] + ob["h"],im_data["height"] -1 )/im_data["height"]*224] for ob in ten_objects]
labels = [ob["names"][0] for ob in ten_objects]
boxes_tensor = torch.tensor(boxes)
image_w_bb = torchvision.utils.draw_bounding_boxes(img_tensor, boxes_tensor, labels=labels, colors="black")
new_image = transforms.ToPILImage()(image_w_bb)
new_image.save("img_bb1.jpg")
i = 6