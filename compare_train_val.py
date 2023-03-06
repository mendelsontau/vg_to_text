import os
import json
import random


f = open(os.path.join("vg_150k_train.json"))
train = json.load(f)
f.close()
f = open(os.path.join("vg_new_improved_text_dataset.json"))
all = json.load(f)
random.shuffle(all)
f.close()
val_samples = []
for sample in all:
    if len(val_samples) == 16:
        break
    in_train = False
    data = sample["image_data"]
    url = data["url"]
    for t in train:
        train_data = t["image_data"]
        url2 = train_data["url"]
        if url == url2:
            in_train = True
            break
    if not in_train:
        val_samples.append(sample)

out_file = open("vg_150k_val.json", "w") 
json.dump(val_samples, out_file, indent = 6)
out_file.close()