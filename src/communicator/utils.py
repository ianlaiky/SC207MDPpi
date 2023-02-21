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

arduino_out = ['SD', 'MC', 'CC', 'EC']
def ardMsgParser(msg):
    # data = msg.split('|')
    # if data[0] in arduino_out:
    return msg
    # else:
        #return None

def setFormat(target, msg):
    return json.dumps({
        'target': target,
        'payload': msg

    })
