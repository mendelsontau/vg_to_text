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
relevant_relationships = sorted_rel_counter[-300:]
out_file = open("top_300_relations.json", "w") 
json.dump(relevant_relationships, out_file, indent = 6)
out_file.close()
non_transitive_relations = {}
for rel in relevant_relationships:
    predicate = rel[0]
    print("is " + predicate + " non-transitive?")
    answer = str(input())
    if answer == "y":
        non_transitive_relations[predicate] = "yes"
    if answer == "n":
        non_transitive_relations[predicate] = "no"

out_file = open("relations_transitivity.json", "w") 
json.dump(non_transitive_relations, out_file, indent = 6)
out_file.close()
