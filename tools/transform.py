import pandas as pd
import json

# read excel file
file_path = './data/raw/事件-汇总.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')

# create a dictionary to store the events and options
JSON_Dic = {"events": []}

for i in range(1, len(df)):
    if pd.notnull(df.loc[i, '事件名称']):
        # create a dictionary for the current scene
        scene_dic = {"id": df.loc[i, 'id'],
                     "description": df.loc[i, '事件文字描述（大约100字）'],
                     "description_short": df.loc[i, '事件名称'],
                     "limit_time_range": df.loc[i, '发生区间'],
                     "the_previous_id": df.loc[i, '前置事件id（仅随机关联事件需要，其他事件填‘/’）'],
                     "options": []}

        # add the options to the current scene
        for j in range(1, 4):
            option_text = df.loc[i, f"选项{j}（每个事件设计2-3个选项）"]
            if pd.notnull(option_text):
                result = eval(df.loc[i, f'Unnamed: {4+3*j}'])
                option_dic = {"text": option_text,
                              "result": {"san": result[0],
                                         "wealth": result[1],
                                         "energy": result[2],
                                         "intimate": result[3],
                                         "academic": result[4]
                                         },
                              "the_next_id": df.loc[i, f"Unnamed: {5+3*j}"]}
                scene_dic["options"].append(option_dic)

        # add the current scene to the events list
        JSON_Dic["events"].append(scene_dic)

# convert JSON_Dic to json
json_str = json.dumps(JSON_Dic, ensure_ascii=False, indent=4)
json_str = json_str.replace("/","")

# write json to file
with open('./data/processed/events.json', 'w', encoding='utf-8') as f:
    f.write(json_str)
