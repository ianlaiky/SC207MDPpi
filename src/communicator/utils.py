import json
from src.Logger import Logger
log = Logger()

def format_for(target, payload):
    return json.dumps({
        'target': target,
        'payload': payload
    })