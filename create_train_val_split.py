import os
import json
from random import sample

f = open("objects.json")
objects = json.load(f)
f = open("attributes.json")
attributes = json.load(f)
f = open("image_data.json")
image_data = json.load(f)
f = open("relationships.json")
relationships = json.load(f)

total_samples = len(objects)
num_val_samples = int(total_samples*0.01)
num_train_samples = total_samples - num_val_samples
all_samples = [i for i in range(total_samples)]
val_samples = sample(all_samples,num_val_samples)


train_objects = []
train_attributes = []
train_image_data = []
train_relationships = []

val_objects = []
val_attributes = []
val_image_data = []
val_relationships = []

for i in range(total_samples):
    if i in val_samples:
        val_objects.append(objects[i])
        val_attributes.append(attributes[i])
        val_image_data.append(image_data[i])
        val_relationships.append(relationships[i])
    else:
        train_objects.append(objects[i])
        train_attributes.append(attributes[i])
        train_image_data.append(image_data[i])
        train_relationships.append(relationships[i])

out_file = open("objects_train.json", "w") 
json.dump(train_objects, out_file, indent = 6)
out_file.close()
out_file = open("attributes_train.json", "w") 
json.dump(train_attributes, out_file, indent = 6)
out_file.close()
out_file = open("image_data_train.json", "w") 
json.dump(train_image_data, out_file, indent = 6)
out_file.close()
out_file = open("relationships_train.json", "w") 
json.dump(train_relationships, out_file, indent = 6)
out_file.close()

out_file = open("objects_val.json", "w") 
json.dump(val_objects, out_file, indent = 6)
out_file.close()
out_file = open("attributes_val.json", "w") 
json.dump(val_attributes, out_file, indent = 6)
out_file.close()
out_file = open("image_data_val.json", "w") 
json.dump(val_image_data, out_file, indent = 6)
out_file.close()
out_file = open("relationships_val.json", "w") 
json.dump(val_relationships, out_file, indent = 6)
out_file.close()
