import json


def json_format(res):
    return json.dumps(res, indent=4,ensure_ascii= False ) # 变成json