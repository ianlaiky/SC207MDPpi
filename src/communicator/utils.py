import json
from src.Logger import Logger

log = Logger()

# Legend:
# To Image = 1
# To Algo = 2
# To Android = 4
# To stm = 8

# Example:
# To Algo and Android: 2 + 4 = 6




def setFormat(source, msg):
    return json.dumps({
        'source': source,
        'data': msg

    })
