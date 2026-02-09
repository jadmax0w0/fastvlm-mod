import os
import json
import ijson
from tqdm import tqdm
from typing import Callable, Optional, Union


# TOTAL_SAMPLES = 10140972
TOTAL_SAMPLES = None


def to_jsonl(
        json_path: str, 
        sample_modifiers: Optional[Union[Callable, list[Callable]]] = None,
        sample_filters: Optional[Union[Callable, list[Callable]]] = None,
):
    if sample_modifiers is not None:
        if not isinstance(sample_modifiers, list):
            sample_modifiers = [sample_modifiers]
    if sample_filters is not None:
        if not isinstance(sample_filters, list):
            sample_filters = [sample_filters]
    
    out_path = os.path.splitext(json_path)[0] + ".jsonl"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("")
    
    with open(json_path, 'r', encoding='utf-8') as jsonfile, open(out_path, 'a', encoding='utf-8') as outfile:
        for i, sample in tqdm(enumerate(ijson.items(jsonfile, "item")), desc="Traversing", total=TOTAL_SAMPLES):
            # Modify
            if sample_modifiers is not None:
                for mod in sample_modifiers:
                    sample = mod(sample, i)
            # Filter
            if sample_filters is not None:
                drop_sample = False
                for filt in sample_filters:
                    if not filt(sample, i):
                        drop_sample = True
                        break
                if drop_sample:
                    print(f"Dropping sample id {i}")
                    continue
            outfile.write(json.dumps(sample) + "\n")


def _modifier_id_to_string(sample: dict, *args, **kwargs):
    if "id" not in sample:
        return sample
    sample['id'] = str(sample['id'])
    return sample

def _modifier_remove_old_id(sample: dict, *args, **kwargs):
    if "old_id" not in sample:
        return sample
    sample.pop("old_id")
    return sample

def _modifier_remove_extra_keys(sample: dict, i: int):
    redundant_key = False
    keys = list(sample.keys())
    for key in keys:
        if key not in ['id', 'conversations', 'image']:
            sample.pop(key)
            redundant_key = True
    if redundant_key:
        # print(f"Removed extra keys in row id {i}: {sample.keys()}")
        pass
    # if len(sample.keys()) > 3:
    #     print(f"Extra keys in row id {i}: {sample.keys()}")
    #     print(f"  Modified: {sample.keys()}")
    return sample

def _modifier_add_none_image_field(sample: dict, i: int):
    if 'image' in sample:
        return sample
    sample['image'] = None
    return sample

def _filter_remove_ill_format(sample: dict, i: int):
    if len(sample.keys()) == 2 and ("id" not in sample or "conversations" not in sample):
        print(f"Ill format in row id {i}: {sample.keys()}")
        return False
    elif len(sample.keys()) == 3 and ("id" not in sample or "conversations" not in sample or "image" not in sample):
        print(f"Ill format in row id {i}: {sample.keys()}")
        return False
    elif len(sample.keys()) != 2 and len(sample.keys()) != 3:
        print(f"Ill format in row id {i}: {sample.keys()}")
        return False
    return True

def _filter_remove_ill_conversation_format(sample: dict, i: int):
    if "conversations" not in sample:
        print(f"Conversation not found in row id {i}")
        return False
    
    if not isinstance(sample['conversations'], list):
        print(f"Conversations is not a list in row id {i}")
        return False
    
    for conv in sample['conversations']:
        if "from" not in conv or "value" not in conv:
            print(f"Conversation does not contain `from` or `value` key in row id {i}: {conv.keys()}")
            return False
        if len(conv) != 2:
            print(f"Conversation has extra keys in row id {i}: {conv.keys()}")
            return False
        if not isinstance(conv['from'], str) or not isinstance(conv['value'], str):
            print(f"Conversation type error in row id {i}")
            return False
    
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str)
    args = parser.parse_args()

    to_jsonl(
        args.path,
        [_modifier_id_to_string, _modifier_remove_extra_keys, _modifier_add_none_image_field],
        [_filter_remove_ill_format, _filter_remove_ill_conversation_format]
    )