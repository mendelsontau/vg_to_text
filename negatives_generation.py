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
import copy

#types of negatives:
#1. replace object and subject in non transitive relations
#2. replace to a false relationship
#3. replace attributes between objects
#4. replace to false attribute

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

def apply_negative_type_4(all_objects_list, all_objects_dict, attributes_annotations):
    success = False
    random.shuffle(all_objects_list)
    for chosen_object in all_objects_list:
        object_id = chosen_object["object_id"]
        if "attributes" not in chosen_object:
            continue
        for att in chosen_object["attributes"]:
            if att not in attributes_annotations:
                continue
            att_annotation = attributes_annotations[att]
            if "negations" not in att_annotation:
                continue
            negatives = att_annotation["negations"]
            if len(negatives) == 0:
                continue
            success = True
            chosen_negative = random.choice(negatives)
            all_objects_dict[str(object_id)]["attributes"][0] = chosen_negative
            break
        if success == True:
            break
    return success, all_objects_dict


def apply_negative_type_3(all_objects_list, all_objects_dict, attributes_annotations):
    success = False
    random.shuffle(all_objects_list)
    for chosen_object in all_objects_list:
        if success == True:
            break
        first_object_id = chosen_object["object_id"]
        if "attributes" not in chosen_object:
            continue
        for att in chosen_object["attributes"]:
            if success == True:
                break
            if att not in attributes_annotations:
                continue
            att_annotation = attributes_annotations[att]
            if "negations" not in att_annotation:
                continue
            negatives = att_annotation["negations"]
            if len(negatives) == 0:
                continue
            for chosen_object2 in all_objects_list:
                if success == True:
                    break
                second_object_id = chosen_object2["object_id"]
                if second_object_id == first_object_id:
                    continue
                if "attributes" not in chosen_object2:
                    continue
                for att2 in chosen_object2["attributes"]:
                    if att2 in negatives and all_objects_dict[str(first_object_id)]["names"][0] != all_objects_dict[str(second_object_id)]["names"][0]:
                        all_objects_dict[str(first_object_id)]["attributes"][0] = att2
                        all_objects_dict[str(second_object_id)]["attributes"][0] = att
                        success = True
                        break
    return success, all_objects_dict


        


def apply_negative_type_1(walks, relations_annotations):
    #find all relationships in the graph
    all_relations = []
    for w in range(len(walks)):
        walk = walks[w]
        for r in range(len(walk)):
            rel = walk[r]
            if rel["object_id"] != -1:
                all_relations.append((rel,w,r))

    random.shuffle(all_relations)
    for rand_rel in all_relations:
        success = False
        rel = rand_rel[0]
        rel_w = rand_rel[1]
        rel_r = rand_rel[2]
        subject_id = rel["subject_id"]
        object_id = rel["object_id"]
        predicate = rel["predicate"]
        if predicate in relations_annotations:
            if relations_annotations[predicate]["symmetry"] == "yes":
                success = True
                walks[rel_w][rel_r]["subject_id"] = object_id
                walks[rel_w][rel_r]["object_id"] = subject_id
        
        if success:
            break
    return success, walks

def apply_negative_type_2(walks, relations_annotations,states,actions):
    #find all relationships in the graph
    all_relations = []
    for w in range(len(walks)):
        walk = walks[w]
        for r in range(len(walk)):
            rel = walk[r]
            if rel["object_id"] != -1:
                all_relations.append((rel,w,r))

    random.shuffle(all_relations)
    for rand_rel in all_relations:
        success = False
        rel = rand_rel[0]
        rel_w = rand_rel[1]
        rel_r = rand_rel[2]
        predicate = rel["predicate"]
        if predicate in relations_annotations:
            if relations_annotations[predicate]["action"] == "no" and relations_annotations[predicate]["state"] == "no" and relations_annotations[predicate]["negations"] == "":
                continue
            negations1 = []
            negations2 = []
            if relations_annotations[predicate]["action"] == "yes":
                negations1 += actions
            if relations_annotations[predicate]["state"] == "yes":
                negations1 += states
            if relations_annotations[predicate]["negations"] != "" :
                negations2 = relations_annotations[predicate]["negations"].split(",")
            if len(negations1) == 0:
                new_predicate = random.choice(negations2)
                success = True
                walks[rel_w][rel_r]["predicate"] = new_predicate
            elif len(negations2) == 0:
                new_predicate = random.choice(negations1)
                success = True
                walks[rel_w][rel_r]["predicate"] = new_predicate
            else:
                rand_bit = random.randint(0,1)
                if rand_bit == 0:
                    new_predicate = random.choice(negations1)
                    success = True
                    walks[rel_w][rel_r]["predicate"] = new_predicate
                else:
                    new_predicate = random.choice(negations2)
                    success = True
                    walks[rel_w][rel_r]["predicate"] = new_predicate

        
        if success:
            break
    return success, walks


f = open("vg_150k_val.json")
data = json.load(f)
f = open("relations_annotations_new.json")
relations_annotations = json.load(f)
f = open("actions.json")
actions = json.load(f)
f = open("states.json")
states = json.load(f)
f = open("attributes_annotations.json")
attributes_annotations = json.load(f)
while True:
    i = random.randint(0,len(data)-1)
    image_url = data[i]["image_data"]["url"]
    crop_dimensions = data[i]["to_crop"]
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
    walks = data[i]["relations"]

    #load objects and choose randomly
    all_objects_dict = data[i]["objects"]
    all_objects_list = []
    for id in all_objects_dict:
        all_objects_list.append(all_objects_dict[id])
    print(create_text_from_graph(walks,all_objects_dict))
    random.shuffle(walks)
    success, new_walks = apply_negative_type_2(copy.deepcopy(walks),relations_annotations,states,actions)
    orig_text = create_text_from_graph(walks,all_objects_dict)
    if success:
        hn_text = create_text_from_graph(new_walks,all_objects_dict)

    print(orig_text) 
    if success:
        print(hn_text)
    t=5


