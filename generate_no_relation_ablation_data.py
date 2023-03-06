import os
import json
import random

f = open(os.path.join("vg_150k_train.json"))
data = json.load(f)

no_relation_data = []

for sample in data:
    all_objects_dict = sample["objects"]
    kept_walks = []
    for k in all_objects_dict:
        element = {"subject_id": int(k), "object_id": -1 , "predicate": "", "relationship_id": -1}
        kept_walks.append([element])
    new_sample = {}
    new_sample["image_data"] = sample["image_data"]
    new_sample["to_crop"] = sample["to_crop"]
    new_sample["relations"] = kept_walks
    new_sample["objects"] = all_objects_dict
    no_relation_data.append(new_sample)

print(len(no_relation_data))
out_file = open("vg_150k_train_no_relation.json", "w") 
json.dump(no_relation_data, out_file, indent = 6)
out_file.close()
