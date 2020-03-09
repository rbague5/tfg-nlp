#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json, io


def convert_data(filename="data.json"):

    with io.open(filename, encoding='utf-8') as train_data:
        train = json.load(train_data)

    TRAIN_DATA = []
    for data in train:
        ents = [tuple(entity) for entity in data['entities']]
        # print(ents)
        # print(f"({data['content']}, 'entities': {ents})")
        TRAIN_DATA.append((data['content'], {'entities': ents}))

    # with open('{}'.format(filename.replace('json', 'txt')), 'w', encoding='utf-8') as write:
    #     write.write(str(TRAIN_DATA))
    # print("Created new Training Data file in current directory")
    return TRAIN_DATA

if __name__ == "__main__":
    convert_data()

