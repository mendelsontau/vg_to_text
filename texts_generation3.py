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
    #remove unwanted relationships
    relationships = [r for r in relationships if r["synsets"] != ['have.v.01'] and r["synsets"] != ['see.v.01'] and r["synsets"] != ['be.v.01'] and r["synsets"] != ['show.v.01'] and r["synsets"] != ['vacate.v.02'] and r["predicate"] != "OF"]

    #all subjects in relevant relationships
    all_rel_subjs = [r["subject_id"] for r in relationships]

    objects = graph["objects"]


    #add center of bounding box and distance from center for every object
    image_center = (image_width/2, image_height/2)
    for obj in objects:
        bb_center = (obj["x"] + 0.5 * obj["w"], obj["y"] + 0.5 * obj["h"])
        coord_dist_from_center = (abs(bb_center[0] - image_center[0]),abs(bb_center[1] - image_center[1]))
        obj["dist_from_center"] = coord_dist_from_center[0]*coord_dist_from_center[0] + coord_dist_from_center[1]*coord_dist_from_center[1]
        obj["bb_center"] = bb_center

    objects_dict = {}
    for objct in objects:
        objects_dict[objct["object_id"]] = objct
    
    #find large objects in the image
    large_objects = [ob for ob in objects if ob["w"] * ob["h"] > 0.035 * image_size]

    #small objects cannot be subjects
    subjects = [ob for ob in objects if ob["w"] * ob["h"] > 0.035 * image_size and ob["object_id"] in all_rel_subjs]


    all_subject_ids = [o["object_id"] for o in subjects]
    relationships = [r for r in relationships if r["subject_id"] in all_subject_ids]

    tries = 0

    crop_in_image = 0
    while True:
        if(tries > 4):
            break 
        relationships_old = relationships
        subjects_old = subjects
        walks = []
        #create a random walk in graph
        if len(subjects) == 0 or len(relationships) == 0:
            break
        walk = find_relation_for_object(relationships, subjects, 0, True)

        walks.append(walk)

        #find all objects in the subgraph created in the walk
        all_objects = []
        for r in walk:
            all_objects.append(r["subject_id"])
            all_objects.append(r["object_id"])
        
        #create a dictionary with all objects and find union of bounding boxes
        min_x = 5000
        min_y = 5000
        max_x = 0
        max_y = 0
        all_objects_dict = {}
        for o in objects:
            if o["object_id"] in all_objects:
                all_objects_dict[o["object_id"]] = o
                if o["x"] < min_x:
                    min_x = o["x"]
                if o["y"] < min_y:
                    min_y = o["y"]
                if o["x"] + o["w"] > max_x:
                    max_x = o["x"] + o["w"]
                if o["y"] + o["h"] > max_y:
                    max_y = o["y"] + o["h"]

        #remove seen subjects and relationships
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
        new_relationships = [rel for rel in new_relationships if (objects_dict[rel["object_id"]]["bb_center"][0] > min_x and objects_dict[rel["object_id"]]["bb_center"][0] < max_x) and (objects_dict[rel["object_id"]]["bb_center"][1] > min_y and objects_dict[rel["object_id"]]["bb_center"][1] < max_y)]
        subjects = new_subjects
        relationships = new_relationships
        all_rel_subjs = [r["subject_id"] for r in relationships]
        subjects = [ob for ob in objects if ob["object_id"] in all_rel_subjs]

        visible_objects = {}
        #add all visible large objects to dict
        for o in large_objects:
            if (o["bb_center"][0] > min_x and o["bb_center"][0] < max_x) and (o["bb_center"][1] > min_y and o["bb_center"][1] < max_y):
                if o["object_id"] not in all_objects_dict:
                    visible_objects[o["object_id"]] = o
        
        #add visible objects to walk
        for k in visible_objects:
            if k in all_objects_dict:
                continue
            extra_walk = find_relation_for_object(relationships, subjects, k, False)
            if len(extra_walk) != 0:
                walks.append(extra_walk)
            else:
                extra_walk = [{"subject_id": k, "object_id": -1, "predicate": "","relationship_id": -1}]
                walks.append(extra_walk)
            new_subjects = []
            new_relationships = []
            for obj in subjects:
                remove = False
                for w in extra_walk:
                    if obj["object_id"] == w["subject_id"] or obj["object_id"] ==  w["object_id"]:
                        remove = True
                        break
                if not remove:
                    new_subjects.append(obj)
            for rel in relationships:
                remove = False
                for w in extra_walk:
                    if rel["relationship_id"] == w["relationship_id"] or rel["subject_id"] == w["subject_id"] or rel["subject_id"] == w["object_id"] or rel["object_id"] == w["subject_id"] or rel["object_id"] == w["object_id"]:
                        remove = True
                        break
                if not remove:
                    new_relationships.append(rel)

     
            subjects = new_subjects
            relationships = new_relationships
            all_rel_subjs = [r["subject_id"] for r in relationships]
            subjects = [ob for ob in objects if ob["object_id"] in all_rel_subjs]
            for r in extra_walk:
                all_objects_dict[r["subject_id"]] = objects_dict[r["subject_id"]]
                if r["object_id"] != -1:
                    all_objects_dict[r["object_id"]] = objects_dict[r["object_id"]]
        
        if len(all_objects_dict) > 10:
            relationships = relationships_old
            subjects = subjects_old
            tries += 1
            continue
        text = ""
        for relations in walks:
            r = relations[0]
            if r["object_id"] == -1:
                if "attributes" in objects_dict[r["subject_id"]]:
                    text += objects_dict[r["subject_id"]]["attributes"][0] + " " + objects_dict[r["subject_id"]]["names"][0]
                else:
                    text += objects_dict[r["subject_id"]]["names"][0]
            else:               
                if "attributes" in objects_dict[r["subject_id"]]:
                    text += objects_dict[r["subject_id"]]["attributes"][0] + " " + objects_dict[r["subject_id"]]["names"][0] + " " + r["predicate"] + " "
                else:
                    text += objects_dict[r["subject_id"]]["names"][0] + " " + r["predicate"] + " "
                if len(relations) != 1:
                    for i in range (1, len(relations)):
                        r = relations[i]
                        if "attributes" in objects_dict[r["subject_id"]]:
                            text += objects_dict[r["subject_id"]]["attributes"][0] + " " + objects_dict[r["subject_id"]]["names"][0] + " " + r["predicate"] + " "
                        else:
                            text += objects_dict[r["subject_id"]]["names"][0] + " " + r["predicate"] + " "
                r = relations[-1]
                if "attributes" in objects_dict[r["object_id"]]:
                    text += objects_dict[r["object_id"]]["attributes"][0] + " " + objects_dict[r["object_id"]]["names"][0]
                else:
                    text += objects_dict[r["object_id"]]["names"][0]
            text += ". "


        #cropped_image = image.crop((min_x, min_y, max_x, max_y))
        #cropped_image.save(os.path.join("examples", "example_" + str(img_counter) + "_" + str(crop_in_image) +  ".jpg"))
        #crop_in_image += 1
        #print(text)
        tries = 0

        #add example to list
        example = {}
        example["image_data"] = im_data
        example["to_crop"] = (min_x, min_y, max_x, max_y)
        example["relations"] = walks
        example["objects"] = all_objects_dict
        all_examples.append(example)
    img_counter += 1
out_file = open("vg_new_text_dataset.json", "w") 
json.dump(all_examples, out_file, indent = 6)
out_file.close()
print(len(all_examples))

        
        

        
                


