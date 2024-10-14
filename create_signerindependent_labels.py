# import csv
# import gzip
# import pickle
# import json
# import os
# from collections import defaultdict

# def read_csv(file_path):
#     data = []
#     with open(file_path, 'r', encoding='utf-8') as f:
#         reader = csv.DictReader(f, delimiter='|')
#         for row in reader:
#             data.append(row)
#     return data

# def load_existing_labels(file_path):
#     with gzip.open(file_path, 'rb') as f:
#         return pickle.load(f)

# def group_by_signer(data):
#     signer_data = defaultdict(list)
#     for row in data:
#         signer_data[row['speaker']].append(row)
#     return signer_data

# def redistribute_data(all_data):
#     all_signer_data = group_by_signer(all_data)
    
#     new_train, new_dev, new_test = [], [], []
#     train_signers, dev_signers, test_signers = set(), set(), set()
    
#     for signer, data in all_signer_data.items():
#         signer_num = int(signer.replace('Signer', ''))
#         if 1 <= signer_num <= 7:
#             new_train.extend(data)
#             train_signers.add(signer)
#         elif signer_num == 8:
#             new_test.extend(data)
#             test_signers.add(signer)
#         elif signer_num == 9:
#             new_dev.extend(data)
#             dev_signers.add(signer)
    
#     print(f"Total samples: {len(all_data)}")
#     print(f"Total signers: {len(all_signer_data)}")
#     print(f"Samples in train set: {len(new_train)}")
#     print(f"Samples in dev set: {len(new_dev)}")
#     print(f"Samples in test set: {len(new_test)}")
    
#     print(f"Train signers: {train_signers}")
#     print(f"Dev signers: {dev_signers}")
#     print(f"Test signers: {test_signers}")
    
#     return new_train, new_dev, new_test

# def ensure_correct_prefix(name, set_prefix):
#     if not name.startswith(f"{set_prefix}/"):
#         return f"{set_prefix}/{name}"
#     return name

# def create_label_dict(data, existing_labels, data_type, src_dir):
#     label_dict = {}
#     set_prefix = data_type
    
#     for row in data:
#         key = row['name']  # Key doesn't have prefix
#         prefixed_name = ensure_correct_prefix(key, set_prefix)
        
#         if key in existing_labels:
#             label_dict[key] = existing_labels[key].copy()
#             # Update the fields that might have changed
#             label_dict[key]['name'] = prefixed_name  # Ensure the name has the correct prefix
#             label_dict[key]['gloss'] = row['orth']
#             label_dict[key]['text'] = row['translation']
#             label_dict[key]['length'] = len(row['orth'].split())
            
#             # Count actual number of frames
#             video_dir = os.path.join(src_dir, set_prefix, key)
#             if os.path.exists(video_dir):
#                 frame_count = len([f for f in os.listdir(video_dir) if f.endswith('.png')])
#                 label_dict[key]['imgs_path'] = [f"{prefixed_name}/images{i:04d}.png" for i in range(1, frame_count + 1)]
#             else:
#                 print(f"Warning: Video directory not found: {video_dir}")
#                 label_dict[key]['imgs_path'] = []
#         else:
#             print(f"Warning: {key} not found in existing labels. Using default values.")
            
#             # Count actual number of frames
#             video_dir = os.path.join(src_dir, set_prefix, key)
#             if os.path.exists(video_dir):
#                 frame_count = len([f for f in os.listdir(video_dir) if f.endswith('.png')])
#                 imgs_path = [f"{prefixed_name}/images{i:04d}.png" for i in range(1, frame_count + 1)]
#             else:
#                 print(f"Warning: Video directory not found: {video_dir}")
#                 imgs_path = []
            
#             label_dict[key] = {
#                 'name': prefixed_name,
#                 'gloss': row['orth'],
#                 'text': row['translation'],
#                 'length': len(row['orth'].split()),
#                 'imgs_path': imgs_path
#             }
#     return label_dict

# def save_gzip_pickle(data, file_path):
#     with gzip.open(file_path, 'wb') as f:
#         pickle.dump(data, f)

# # Paths
# csv_dir = '/mnt/c/Research/Dataset/phoenix-2014_o/PHOENIX-2014-T-release-v3/PHOENIX-2014-T/annotations/manual'
# src_dir = '/mnt/c/Research/Dataset/phoenix-2014_o/PHOENIX-2014-T-release-v3/PHOENIX-2014-T/features/SI_fullFrame-210x260px'

# # Read and combine all CSV files
# all_csv = (
#     read_csv(os.path.join(csv_dir, 'PHOENIX-2014-T.train.corpus.csv')) +
#     read_csv(os.path.join(csv_dir, 'PHOENIX-2014-T.dev.corpus.csv')) +
#     read_csv(os.path.join(csv_dir, 'PHOENIX-2014-T.test.corpus.csv'))
# )

# print(f"Total samples in all CSV files: {len(all_csv)}")

# # Load existing train labels
# existing_train_labels = load_existing_labels('./data/Phonexi-2014T/labels.train')

# print(f"Samples in existing train labels: {len(existing_train_labels)}")

# # Redistribute data
# new_train, new_dev, new_test = redistribute_data(all_csv)

# # Create label dictionaries
# train_dict = create_label_dict(new_train, existing_train_labels, 'SI_train', src_dir)
# dev_dict = create_label_dict(new_dev, existing_train_labels, 'SI_dev', src_dir)
# test_dict = create_label_dict(new_test, existing_train_labels, 'SI_test', src_dir)

# # Save new label files
# save_gzip_pickle(train_dict, './data/Phonexi-2014T/newlabels.train')
# save_gzip_pickle(dev_dict, './data/Phonexi-2014T/newlabels.dev')
# save_gzip_pickle(test_dict, './data/Phonexi-2014T/newlabels.test')

# print(f"New label files created:")
# print(f"Train: {len(train_dict)} samples")
# print(f"Dev: {len(dev_dict)} samples")
# print(f"Test: {len(test_dict)} samples")

# # Print a sample entry from each set
# print("\nSample entries:")
# for set_name, data_dict in [("Train", train_dict), ("Dev", dev_dict), ("Test", test_dict)]:
#     if data_dict:
#         sample_key = next(iter(data_dict))
#         print(f"\n{set_name} sample:")
#         print(f"Key: {sample_key}")
#         print("Value:", json.dumps(data_dict[sample_key], indent=2))
#     else:
#         print(f"\n{set_name} set is empty!")


import csv
import gzip
import pickle
import os
from collections import defaultdict

def read_csv(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='|')
        for row in reader:
            data.append(row)
    return data

def create_label_dict(all_data, src_dir, set_type):
    label_dict = {}
    for row in all_data:
        key = row['name']
        video_dir = os.path.join(src_dir, set_type, key)
        
        if os.path.exists(video_dir):
            frame_count = len([f for f in os.listdir(video_dir) if f.endswith('.png')])
            prefixed_key = f"{set_type}/{key}"
            imgs_path = [f"{prefixed_key}/images{i:04d}.png" for i in range(1, frame_count + 1)]
            
            label_dict[prefixed_key] = {
                "name": prefixed_key,
                "gloss": row['orth'],
                "text": row['translation'],
                "length": len(row['orth'].split()),
                "imgs_path": imgs_path
            }
    
    return label_dict

def save_gzip_pickle(data, file_path):
    with gzip.open(file_path, 'wb') as f:
        pickle.dump(data, f)

# Paths
csv_dir = '/mnt/c/Research/Dataset/phoenix-2014_o/PHOENIX-2014-T-release-v3/PHOENIX-2014-T/annotations/manual'
src_dir = '/mnt/c/Research/Dataset/phoenix-2014_o/PHOENIX-2014-T-release-v3/PHOENIX-2014-T/features/SI_fullFrame-210x260px'

# Read and combine all CSV files
all_csv = (
    read_csv(os.path.join(csv_dir, 'PHOENIX-2014-T.train.corpus.csv')) +
    read_csv(os.path.join(csv_dir, 'PHOENIX-2014-T.dev.corpus.csv')) +
    read_csv(os.path.join(csv_dir, 'PHOENIX-2014-T.test.corpus.csv'))
)

# Create label dictionaries
train_dict = create_label_dict(all_csv, src_dir, 'train')
dev_dict = create_label_dict(all_csv, src_dir, 'dev')
test_dict = create_label_dict(all_csv, src_dir, 'test')

# Save label files
save_gzip_pickle(train_dict, './data/Phonexi-2014T/SI_labels.train')
save_gzip_pickle(dev_dict, './data/Phonexi-2014T/SI_labels.dev')
save_gzip_pickle(test_dict, './data/Phonexi-2014T/SI_labels.test')

print(f"New label files created:")
print(f"Train: {len(train_dict)} samples")
print(f"Dev: {len(dev_dict)} samples")
print(f"Test: {len(test_dict)} samples")

# Print a sample entry from each set
import json
for set_name, data_dict in [("Train", train_dict), ("Dev", dev_dict), ("Test", test_dict)]:
    if data_dict:
        sample_key = next(iter(data_dict))
        print(f"\n{set_name} sample:")
        print(json.dumps({sample_key: data_dict[sample_key]}, indent=2))
    else:
        print(f"\n{set_name} set is empty!")