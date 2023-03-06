import os
import json
import random

f = open(os.path.join("vg_150k_train.json"))
data = json.load(f)


for level in [1,2,3]:
    not_dense_data = []
    per_level = 0.1 + (level-1) * 0.3
    for sample in data:
        all_objects_dict = sample["objects"]
        walks = sample["relations"]
        num_elements = len(walks)
        elements_to_keep = max(int(per_level*num_elements),1)
        possibilities = [i for i in range(num_elements)]
        walks_to_keep = random.sample(possibilities,elements_to_keep)
        walks_to_keep.sort()
        kept_walks = [walks[i] for i in walks_to_keep]
        kept_objects_dict = {}
        for kw in kept_walks:
            for w in kw:
                subject_id = w["subject_id"]
                object_id = w["object_id"]
                if str(subject_id) not in kept_objects_dict:
                    kept_objects_dict[str(subject_id)] = all_objects_dict[str(subject_id)]
                if object_id != -1:
                    if str(object_id) not in kept_objects_dict:
                        kept_objects_dict[str(object_id)] = all_objects_dict[str(object_id)]
        
        new_sample = {}
        new_sample["image_data"] = sample["image_data"]
        new_sample["to_crop"] = sample["to_crop"]
        new_sample["relations"] = kept_walks
        new_sample["objects"] = kept_objects_dict
        not_dense_data.append(new_sample)

    print(len(not_dense_data))
    out_file = open("vg_150k_train_no_dense_" + str(level) + ".json", "w") 
    json.dump(not_dense_data, out_file, indent = 6)
    out_file.close()
