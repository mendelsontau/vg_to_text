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
    count = 0
    if first_call:
        while True:
            rnd_object = objects[count]
            subj_id = rnd_object["object_id"]
            relevant_relationships = []
            for r in relationships:
                if r["subject_id"] == subj_id:
                    relevant_relationships.append(r)
            if len(relevant_relationships) == 0:
                count += 1
                continue
            else:
                chosen_rel = random.choice(relevant_relationships)
                predicate = chosen_rel["predicate"]
                relationship_id = chosen_rel["relationship_id"]
                obj_id = chosen_rel["object_id"]
                relationships = [r for r in relationships if r["object_id"] != subj_id and r["subject_id"] != subj_id]
                objects = [o for o in objects if o["object_id"] != subj_id]
                return [{"subject_id": subj_id, "object_id": obj_id, "predicate": predicate,"relationship_id": relationship_id}] + find_relation_for_object(relationships, objects, obj_id, False)
    else:
        present = False
        for s in objects:
            if s["object_id"] == subj_id:
                present = True
        if present == False:
            return []
        relevant_relationships = []
        for r in relationships:
            if r["subject_id"] == subj_id:
                relevant_relationships.append(r)
        
        if len(relevant_relationships) == 0:
            return []
        else:
            chosen_rel = random.choice(relevant_relationships)
            predicate = chosen_rel["predicate"]
            relationship_id = chosen_rel["relationship_id"]
            obj_id = chosen_rel["object_id"]
            relationships = [r for r in relationships if r["object_id"] != subj_id and r["subject_id"] != subj_id]
            objects = [o for o in objects if ["object_id"] != subj_id]
            return [{"subject_id": subj_id, "object_id": obj_id, "predicate": predicate,"relationship_id": relationship_id}] + find_relation_for_object(relationships, objects, obj_id, False)


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
    image_size = image_height * image_width
    relationships = graph["relationships"]
    relationships = [r for r in relationships if r["synsets"] != ['have.v.01'] and r["synsets"] != ['see.v.01'] and r["synsets"] != ['be.v.01'] and r["synsets"] != ['show.v.01'] and r["synsets"] != ['vacate.v.02'] and r["predicate"] != "OF"]
    all_rel_subjs = [r["subject_id"] for r in relationships]
    objects = graph["objects"]
    image_center = (image_width/2, image_height/2)
    for obj in objects:
        bb_center = (obj["x"] + 0.5 * obj["w"], obj["y"] + 0.5 * obj["h"])
        coord_dist_from_center = (abs(bb_center[0] - image_center[0]),abs(bb_center[1] - image_center[1]))
        obj["dist_from_center"] = coord_dist_from_center[0]*coord_dist_from_center[0] + coord_dist_from_center[1]*coord_dist_from_center[1]
    objects = sorted(objects, key=lambda d: d['dist_from_center']) 
    subjects = [ob for ob in objects if ob["w"] * ob["h"] > 0.035 * image_size and ob["object_id"] in all_rel_subjs]
    all_subject_ids = [o["object_id"] for o in subjects]
    relationships = [r for r in relationships if r["subject_id"] in all_subject_ids]
    walks = []
    while True:
    #create a random walk in graph
        if len(subjects) == 0 or len(relationships) == 0:
            break
        walk = find_relation_for_object(relationships, subjects, 0, True)
        walks.append(walk)
        new_subjects = []
        new_relationships = []
        for obj in subjects:
            remove = False
            for w in walk:
                if obj["object_id"] == w["subject_id"] or obj["object_id"] ==  w["object_id"]:
                    remove = True
                    break
            if not remove:
                new_subjects.append(obj)
        for rel in relationships:
            remove = False
            for w in walk:
                if rel["relationship_id"] == w["relationship_id"] or rel["subject_id"] == w["subject_id"] or rel["subject_id"] == w["object_id"] or rel["object_id"] == w["subject_id"] or rel["object_id"] == w["object_id"]:
                    remove = True
                    break
            if not remove:
                new_relationships.append(rel)
        
        subjects = new_subjects
        relationships = new_relationships
        all_rel_subjs = [r["subject_id"] for r in relationships]
        subjects = [ob for ob in objects if ob["object_id"] in all_rel_subjs]

    #find all objects in subgraph
    all_objects = []
    all_subjects = []
    relations = [item for sublist in walks for item in sublist]
    for r in relations:
        all_objects.append(r["subject_id"])
        all_subjects.append(r["subject_id"])
        all_objects.append(r["object_id"])
    all_object_names = {}
    all_object_attributes = {}
    objects_for_example = []
    for o in objects:
        if o["object_id"] in all_objects:
            objects_for_example.append(o)
            all_object_names[str(o["object_id"])] = o["names"][0]
            if  "attributes" in o:
                all_object_attributes[str(o["object_id"])] = o["attributes"][0]
    #create text
    text = ""
    for relations in walks:
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
        text += ". "
    image.save(os.path.join("examples", "example_" + str(img_counter) + ".jpg"))
    img_counter += 1
    print(text)
    t = 5
        

        
                


