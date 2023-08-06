import json

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return flat(obj)
            
        return json.JSONEncoder.default(self, obj)