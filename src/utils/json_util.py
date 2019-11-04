import decimal
import json
from json.decoder import JSONDecodeError


class JsonUtil:

    @staticmethod
    def loads(data):
        return json.loads(data, parse_float=decimal.Decimal)

    @staticmethod
    def dumps(data):
        return json.dumps(data, cls=DecimalEncoder)

    @staticmethod
    def is_valid_json(src):
        if src is None:
            return False

        try:
            res = json.loads(src)
            if isinstance(res, dict) or isinstance(res, list):
                return True
            return False
        except JSONDecodeError:
            return False


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
