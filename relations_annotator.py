from PIL import Image
import re
import torchvision.transforms as transforms
import torchvision
from torchvision.transforms import InterpolationMode
import numpy as np
import random
# Import the image editing libraries from PIL
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json


f = open("relationships.json")
relationships = json.load(f)
relationship_counter = {}
for img in relationships:
    for r in img["relationships"]:
        predicate = r["predicate"]
        if r["synsets"] != ['have.v.01'] and r["synsets"] != ['see.v.01'] and r["synsets"] != ['be.v.01'] and r["synsets"] != ['show.v.01'] and r["synsets"] != ['vacate.v.02'] and r["predicate"] != "OF":
            if predicate in relationship_counter:
                relationship_counter[predicate] += 1
            else:
                relationship_counter[predicate] = 1
sorted_rel_counter = sorted(relationship_counter.items(), key=lambda x:x[1])
relevant_relationships = sorted_rel_counter[-500:]
f = open("relations_annotations.json")
relations_annotations = json.load(f)
relations_annotations_new = {}
actions = []
states = [] 
counter = 0
for rel in relevant_relationships:
    print(counter)
    predicate = rel[0]
    rel_dict = {}
    if predicate in relations_annotations:
        rel_dict["symmetry"] = relations_annotations[predicate]["symmetry"]
        rel_dict["negations"] = relations_annotations[predicate]["negations"]
    else:
        print("is " + predicate + " non-transitive?")
        answer = str(input())
        if answer == "y":
            rel_dict["symmetry"] = "yes"
        if answer == "n":
            rel_dict["symmetry"] = "no"
        print("type negations for the relationship " + predicate)
        answer = str(input())
        answer.split(",")
        rel_dict["negations"] = answer
    print("is " + predicate + " an action?")
    answer = str(input())
    if answer == "y":
        rel_dict["action"] = "yes"
        actions.append(predicate)
    if answer == "n":
        rel_dict["action"] = "no"
    print("is " + predicate + " a state?")
    answer = str(input())
    if answer == "y":
        rel_dict["state"] = "yes"
        states.append(predicate)
    if answer == "n":
        rel_dict["state"] = "no"
    relations_annotations_new[predicate] = rel_dict
    counter += 1

    out_file = open("relations_annotations_new.json", "w") 
    json.dump(relations_annotations_new, out_file, indent = 6)
    out_file.close()
    out_file = open("actions.json", "w") 
    json.dump(actions, out_file, indent = 6)
    out_file.close()
    out_file = open("states.json", "w") 
    json.dump(states, out_file, indent = 6)
    out_file.close()