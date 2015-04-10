import json

def printThisJson(_printThisNicely):
    print json.dumps(_printThisNicely, sort_keys=True, indent=4, separators=(',', ': '))