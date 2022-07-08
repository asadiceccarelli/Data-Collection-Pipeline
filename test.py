import os
import shutil
import json

path = '/Users/asadiceccarelli/Documents/AiCore/Data-Collection-Pipeline/raw_data/testt33'
if not os.path.exists(path):
    os.makedirs(path)
else:
    shutil.rmtree(path)           
    os.makedirs(path)


data = {'r': 4, 'e': 5, 'c': 7}

json_string = json.dumps(data)
print(json_string)

with open('/Users/asadiceccarelli/Documents/AiCore/Data-Collection-Pipeline/raw_data/testt33/json_data.json', 'w') as outfile:
    outfile.write(json_string)