import os
import json
import copy
from tqdm import tqdm


def _filter_sample(sample: dict):
    try:
        image = sample['image']
        if isinstance(image, str):
            return True, sample
        elif isinstance(image, list) and len(image) == 1:
            sample_ = copy.deepcopy(sample)
            sample_['image'] = sample_['image'][0]
            return True, sample_
        else:
            return False, sample

    except Exception as e:
        if "image" not in sample and "images" not in sample:  # pure textual modal
            return True, sample
        
        sample_ = copy.deepcopy(sample)
        sample_['error'] = str(e)
        return False, sample_


def filter_single_image(path: str):
    samples = []
    print("Reading file")
    with open(path, "r", encoding='utf-8') as f:
        samples = json.loads(f.read())
    
    dropped_samples = []
    filtered_samples = []
    for sample in tqdm(samples, desc="Filtering samples", total=len(samples)):
        kept, sample_ = _filter_sample(sample)
        if kept:
            filtered_samples.append(sample_)
        else:
            dropped_samples.append(sample_)
    
    return filtered_samples, dropped_samples


def filter_single_image_stream(read_path: str, filtered_save_path: str = None, dropped_save_path: str = None):
    import ijson
    from datetime import datetime

    cur_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    if filtered_save_path is None:
        filtered_save_path = os.path.splitext(read_path)[0] + f"_filtered_{cur_time}.jsonl"
    if dropped_save_path is None:
        dropped_save_path = os.path.splitext(read_path)[0] + f"_dropped_{cur_time}.jsonl"

    dropped_count = 0
    filtered_count = 0

    print("Preparing output files...")
    with open(filtered_save_path, "w", encoding="utf-8") as f:
        f.write("")
    with open(dropped_save_path, "w", encoding="utf-8") as f:
        f.write("")
    
    with open(read_path, "r", encoding='utf-8') as jsonfile, \
            open(filtered_save_path, "a", encoding="utf-8") as ffile, \
            open(dropped_save_path, "a", encoding="utf-8") as dfile:
        
        for sample in tqdm(ijson.items(jsonfile, "item"), desc="Filtering samples", total=10140972):
            kept, sample_ = _filter_sample(sample)
            if kept:
                ffile.write(json.dumps(sample_) + "\n")
                filtered_count += 1
            else:
                dfile.write(json.dumps(sample_) + "\n")
                dropped_count += 1
        
        print("Closing files...")
    
    return filtered_count, dropped_count


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, default="mammoth_si_10M.json")
    args = parser.parse_args()

    # filtered_samples, dropped_samples = filter_single_image(args.path)

    # with open(os.path.splitext(args.path)[0] + "_filtered.json", "w", encoding='utf-8') as f:
    #     json.dump(filtered_samples, f, indent=4)
    # with open(os.path.splitext(args.path)[0] + "_dropped.json", "w", encoding="utf-8") as f:
    #     json.dump(dropped_samples, f, indent=4)

    fcount, dcount = filter_single_image_stream(args.path)
    print(f"Kept count: {fcount}, dropped count: {dcount}")