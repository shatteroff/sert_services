import json
from datetime import datetime

from sqlalchemy.ext.declarative import DeclarativeMeta

from db_models import Request, Margin


class AlchemyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Request):
            obj.user_name = obj.user_.name
        elif isinstance(obj, Margin):
            obj.name = obj.user_.name
            obj.workplace = obj.user_.workplace
            obj.alias = obj.user_.alias
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and not x.endswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                if isinstance(data, datetime):
                    data = data.isoformat(timespec='seconds')
                try:
                    json.dumps(data)  # this will fail on non-encodable values, like other classes
                    if isinstance(obj, Request) and field == 'insert_dt':
                        fields['date'] = data
                    else:
                        fields[field] = data
                except TypeError:
                    # print(f"Can't encode var {field} type {type(data)}")
                    _ = 0
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)
