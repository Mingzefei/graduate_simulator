# read information from excel and transform it to json

import pandas as pd
import json
import sys

# read excel file
file_path = '事件-王鹤翔.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')
with open('event.json', 'a', encoding='utf-8') as f:
    f.truncate(0)
# print(df.keys())
JSON_Dic = {}
for i in range(1, len(df)):
    if pd.notnull(df.loc[i, '事件名称']):
        JSON_Dic["scenes"] = df.loc[i, '事件名称']
        JSON_Dic["id"] = df.loc[i, 'id']
        JSON_Dic["description"] = df.loc[i, '事件文字描述（大约100字）']
        JSON_Dic["limit_time_range"] = df.loc[i, '发生区间']
        JSON_Dic["the_previous_id"] = df.loc[i, '前置事件id（仅随机关联事件需要，其他事件填‘/’）']
        JSON_Dic["options_1"] = df.loc[i, '选项1（每个事件设计2-3个选项）'], df.loc[i, 'Unnamed: 7'], df.loc[i, 'Unnamed: 8']
        JSON_Dic["options_2"] = df.loc[i, '选项2（每个事件设计2-3个选项）'], df.loc[i, 'Unnamed: 10'], df.loc[i, 'Unnamed: 11']
        if pd.notnull(df.loc[i, '选项3（每个事件设计2-3个选项）']):
            JSON_Dic["options_3"] = df.loc[i, '选项3（每个事件设计2-3个选项）'], df.loc[i, 'Unnamed: 13'], df.loc[i, 'Unnamed: 14']

        # convert JSON_Dic to json
        json_str = json.dumps(JSON_Dic, ensure_ascii=False, indent=4)
        json_str = json_str.replace("/", "")
        # write json to file
        with open('event.json', 'a', encoding='utf-8') as f:
            f.write(json_str + ',\n')
