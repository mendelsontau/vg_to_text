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

def find_relation_for_object(relationships, objects, subj_id = None, first_call = False):
    #randomly pick object
    if first_call:
        while True:
            rnd_object = random.choice(objects)
            subj_id = rnd_object["object_id"]
            relevant_relationships = []
            for r in relationships:
                if r["subject_id"] == subj_id:
                    relevant_relationships.append(r)
            if len(relevant_relationships) == 0:
                continue
            else:
                chosen_rel = random.choice(relevant_relationships)
                predicate = chosen_rel["predicate"]
                obj_id = chosen_rel["object_id"]
                relationships = [r for r in relationships if r["object_id"] != subj_id and r["subject_id"] != subj_id]
                objects = [o for o in objects if o["object_id"] != subj_id]
                return [{"subject_id": subj_id, "object_id": obj_id, "predicate": predicate}] + find_relation_for_object(relationships, objects, obj_id, False)
    else:
        relevant_relationships = []
        for r in relationships:
            if r["subject_id"] == subj_id:
                relevant_relationships.append(r)
        
        if len(relevant_relationships) == 0:
            return []
        else:
            chosen_rel = random.choice(relevant_relationships)
            predicate = chosen_rel["predicate"]
            obj_id = chosen_rel["object_id"]
            relationships = [r for r in relationships if r["object_id"] != subj_id and r["subject_id"] != subj_id]
            objects = [o for o in objects if ["object_id"] != subj_id]
            return [{"subject_id": subj_id, "object_id": obj_id, "predicate": predicate}] + find_relation_for_object(relationships, objects, obj_id, False)

def bb_not_in_image(boundaries, bb):
    #min_x > max_x
    if bb[0] > boundaries[2]:
        return True
    
    #min_y > max_y
    if bb[1] > boundaries[3]:
        return True

    if bb[2] < boundaries[0]:
        return True

    if bb[3] < boundaries[1]:
        return True

    return False



random.seed(10)
#load scene graphs and image data
f = open("scene_graphs.json")
graphs = json.load(f)
f = open("image_data.json")
image_data = json.load(f)
max_objects_in_scene = 0

all_examples = []
img_counter = 0
for graph in graphs:
    print(img_counter)
    #extract image data
    im_data = image_data[img_counter]

    image_url = im_data["url"]
    url_parts = re.split("/|//", image_url)
    fixed_url = os.path.join(url_parts[5],url_parts[5],url_parts[6])
    image = Image.open(fixed_url)


    image_width = im_data["width"]
    image_height = im_data["height"]
    relationships = graph["relationships"]
    relationships = [r for r in relationships if r["synsets"] != ['have.v.01'] and r["synsets"] != ['see.v.01'] and r["synsets"] != ['be.v.01'] and r["synsets"] != ['show.v.01'] and r["synsets"] != ['vacate.v.02']]
    objects = graph["objects"]
    if len(objects) == 0 or len(relationships) == 0:
        img_counter += 1
        continue

    #create a random walk in graph
    relations = find_relation_for_object(relationships, objects, 0, True)


    #find all objects in subgraph
    all_objects = []
    all_subjects = []
    for r in relations:
        all_objects.append(r["subject_id"])
        all_subjects.append(r["subject_id"])
        all_objects.append(r["object_id"])
    all_object_names = {}
    all_object_attributes = {}
    all_object_bb = {}
    min_x = 5000
    min_y = 5000
    max_x = 0
    max_y = 0
    objects_for_example = []
    for o in objects:
        if o["object_id"] in all_objects:
            objects_for_example.append(o)
            all_object_names[str(o["object_id"])] = o["names"][0]
            if  "attributes" in o:
                all_object_attributes[str(o["object_id"])] = o["attributes"][0]
            all_object_bb[str(o["object_id"])] = [o["x"],o["y"],o["x"] + o["w"],o["y"] + o["h"]]
        if o["object_id"] in all_subjects:
            if o["x"] < min_x:
                min_x = o["x"]
            if o["y"] < min_y:
                min_y = o["y"]
            if o["x"] + o["w"] > max_x:
                max_x = o["x"] + o["w"]
            if o["y"] + o["h"] > max_y:
                max_y = o["y"] + o["h"]
    widening_per = 0.1
    min_x = max(0, int(min_x - widening_per * image_width))
    min_y = max(0, int(min_y - widening_per * image_height))
    max_x = min(image_width, int(max_x + widening_per * image_width))
    max_y = min(image_height, int(max_y + widening_per * image_height))

    to_crop = (min_x, min_y, max_x, max_y)

    if len(objects_for_example) >  max_objects_in_scene:
        max_objects_in_scene = len(objects_for_example)
    #check that all objects are visible in image
    missing_objects = False
    for bb in all_object_bb:
        if bb_not_in_image(to_crop, all_object_bb[bb]):
            missing_objects = True
            break
    
    if missing_objects:
        img_counter += 1
        continue



    #create text
    text = ""
    r = relations[0]
    if str(r["subject_id"]) in all_object_attributes:
        text += all_object_attributes[str(r["subject_id"])] + " " + all_object_names[str(r["subject_id"])] + " " + r["predicate"]
    else:
        text += all_object_names[str(r["subject_id"])] + " " + r["predicate"]
    if len(relations) != 1:
        for i in range (1, len(relations)):
            r = relations[i]
            if str(r["subject_id"]) in all_object_attributes:
                text += " " +  all_object_attributes[str(r["subject_id"])] + " " + all_object_names[str(r["subject_id"])] + " " + r["predicate"]
            else:
                text += " " +  all_object_names[str(r["subject_id"])] + " " + r["predicate"]
    if str(relations[-1]["object_id"]) in all_object_attributes:
        text += " " + all_object_attributes[str(relations[-1]["object_id"])] + " " + all_object_names[str(relations[-1]["object_id"])]
    else:
        text += " " + all_object_names[str(relations[-1]["object_id"])]  

    example = {}
    example["image_data"] = im_data
    example["objects"] = objects_for_example
    example["to_crop"] = to_crop
    example["text"] = text
    example["relations"] = relations
    all_examples.append(example)

    #if img_counter % 10 == 0:

    #    image.save(os.path.join("examples", "example_" + str(img_counter) + "_orig.jpg"))

    #    image = image.crop(to_crop)

        # Open the image, expand it 
    #    expanded_image = ImageOps.expand(image, border=20, fill='white')

        # Add define a new font to write in the border
    #    font = ImageFont.load_default()

        # Instantiate draw object & add desired text
    #    draw_object = ImageDraw.Draw(expanded_image)
    #    draw_object.text(xy=(5,5), text=text, fill=(0,0,0), font=font)

    #    # Save the image
    #    expanded_image.save(os.path.join("examples", "example_" + str(img_counter) + ".jpg"))
    img_counter += 1
out_file = open("vg_text_dataset.json", "w") 
json.dump(all_examples, out_file, indent = 6)
out_file.close()
print(len(all_examples))
print(max_objects_in_scene)

            






