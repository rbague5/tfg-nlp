#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List

import pandas as pd

def find_entity_txt(content, entity):
    # print(f"Content: {content}")
    print(f"{content[entity[0]:entity[1]]}")


def find_entities_text():
    f = open("../documents/STS_175_2020.txt", "r", encoding="utf8")
    file = f.read()


    for tuple in txt_proces:
        print(tuple)
        # print(f"Tuple 0: {tuple[0]}, type {type(tuple[0])}")
        # print(f"Tuple 1: {tuple[1]}, type {type(tuple[1])}, len {len(tuple[1])}")
        # print(f"Entities: {tuple[1]['entities']}")
        # print(f"{tuple[0]}")
        if len(tuple[1]['entities']) is 0:
            print("No entity found")

        if len(tuple[1]['entities']) is not 0:
            for i in tuple[1]['entities']:
                # print(f"Start: {i[0]}, end: {i[1]}")
                find_entity_txt(content=tuple[0], entity=i)
        # print(f"Entities: {tuple[1]['entities']}, type {type(tuple[1]['entities'])}, len {len(tuple[1]['entities'])}")
        # print(f"Start {tuple[1]['entities'][0]}, end {tuple[1]['entities'][1]}")
        print()


def find_entities_json():
    df = pd.read_json(r'D:\Projectes\cognition-intelligence\Cognition\python\laboratory\labeling_spacy\data.json',
                      encoding="utf8")
    # for content, entity in zip(df['content'], df['entities']):
    #     print(f"CONTENT {content} ---> ENTITIES: {entity}")
    #     find_entities_json(content, entity)

def find_entity(content, entity):
    for i in entity:
        # print(i)
        # print(f"Start: {i[0]}, end: {i[1]}")
        print(content[i[0]:i[1]])
    print()


if __name__ == "__main__":

    find_entities_json()
    find_entities_text()