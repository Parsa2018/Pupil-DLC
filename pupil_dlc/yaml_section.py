# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 21:36:32 2024

@author: parsa.seyfourian
"""
import yaml

def replace_yaml_section(config_path):
    with open(config_path, 'r') as file:
        data = yaml.safe_load(file)
        
    
    # Define the new content
    new_bodyparts = [
        'Point1', 'Point2', 'Point3', 'Point4', 'Point5', 'Point6', 
        'Point7', 'Point8', 'Point9', 'Point10', 'Point11', 'Point12', 
        'Eye1', 'Eye2', 'Eye3', 'Eye4'
    ]
    new_skeleton = [
        ['Point1', 'Point2'], ['Point2', 'Point3'], ['Point3', 'Point4'],
        ['Point4', 'Point5'], ['Point5', 'Point6'], ['Point6', 'Point7'],
        ['Point7', 'Point8'], ['Point8', 'Point9'], ['Point9', 'Point10'],
        ['Point10', 'Point11'], ['Point11', 'Point12'], ['Point12', 'Point1'],
        ['Eye1', 'Eye2'], ['Eye2', 'Eye3'], ['Eye3', 'Eye4'], ['Eye4', 'Eye1']
    ]
    
    # Replace the relevant sections
    data['bodyparts'] = new_bodyparts
    data['skeleton'] = new_skeleton
    data['dotsize'] = 2
    
    # Write the modified content back to the file
    with open(config_path, 'w') as file:
        yaml.dump(data, file, default_flow_style=False, sort_keys=False)