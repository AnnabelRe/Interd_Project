import os
import pandas as pd
import numpy as np
import warnings
import seaborn as sns
from names_dataset import NameDataset
import time
import datetime 
import re


def classify(names):
    nd = NameDataset()
    result = {}
    
    for name in names:
        
        full_name = name.split(" ")
        
        if len(full_name) != 1 : 
             
            first = re.sub(r'[^a-zA-Z0-9.,]', '', full_name[1])

            second = None
            if len(full_name)>2:
                second = re.sub(r'[^a-zA-Z0-9.,]', '', full_name[2])

            if ((first != None) and (isinstance(first, str))):
                #print(first)
                first_all = nd.search(first)

                if((first_all.get('first_name') != None) and (len(first)>1)):
                    gender_all = first_all.get('first_name')["gender"]
                    gender_item = max((v,k) for k,v in gender_all.items())
                    #print(gender_item)
                    #print(gender_item[1])
                    result[name]= gender_item[1]

                else:
                    #print(second)
                    if ((second != None) and (isinstance(second, str))):
                        second_all = nd.search(second)

                        if((second_all.get('first_name')) != None and (len(second)>1)):
                            gender_all = second_all.get('first_name')["gender"]
                            #print(gender_all)
                            gender_item = max((v,k) for k,v in gender_all.items())
                            result[name] = gender_item[1]

                        else: 
                            result[name] = "na"
                    else: 
                        result[name]= "na"
            else: 
                result[name]="na"

    return result


