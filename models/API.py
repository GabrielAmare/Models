import json
from flask import request, jsonify
from flask_login import current_user
from .utils import DebugClass


class BaseAPI(DebugClass):
    @staticmethod
    def parse_request():
        try:
            request_data = json.loads(request.data, encoding="utf-8")
            data = request_data.get('data', {})
            format = request_data.get('format', {})
        except:
            data, format = dict(request.form), {}
        return data, format

    @classmethod
    def include_parsed_request(cls, method):
        def new_method(self, *args, **kwargs):
            data, format = cls.parse_request()
            return method(self, data, format, *args, **kwargs)

        return new_method

    @staticmethod
    def response(status, data=None, message=None):
        try:
            return jsonify(dict(status=status, data=data, message=message))
        except Exception as e:
            return jsonify(dict(status="error", data=None, message=str(e)))

    @classmethod
    def success(cls, data):
        return cls.response(status="success", data=data)

    @classmethod
    def error(cls, message):
        return cls.response(status="error", message=message)

    def debug_message(self, message):
        if self.debug:
            print(f"[{self.__class__.__name__}] {message}")


class API(BaseAPI):
    def __init__(self, crud, debug=True):
        super().__init__(debug)
        self.crud = crud

    def build_routes(self, api):
        name = self.crud.model.__name__.lower()
        api.add_url_rule(rule=f"/json/{name}/new", endpoint=f"POST_{name}", view_func=self.POST, methods=['POST'])
        api.add_url_rule(rule=f"/json/{name}/<uid>", endpoint=f"GET_{name}", view_func=self.GET, methods=['GET'])
        api.add_url_rule(rule=f"/json/{name}/<uid>", endpoint=f"PUT_{name}", view_func=self.PUT, methods=['PUT'])
        api.add_url_rule(rule=f"/json/{name}/<uid>", endpoint=f"DELETE_{name}", view_func=self.DELETE,
                         methods=['DELETE'])

    def REQUEST(self, uid, data, format):
        try:
            request_data = dict(user=current_user, uid=uid, data=data, format=format)
            client_data = self.crud.apply_client(**request_data)
            return self.success(client_data)
        except Exception as e:
            return self.error(str(e))

    @BaseAPI.include_parsed_request
    def GET(self, _data, format, uid):
        self.debug_message(f"GET : {self.crud.model.__name__}:{uid}")
        return self.REQUEST(uid=int(uid), data={}, format=format)

    @BaseAPI.include_parsed_request
    def POST(self, data, format):
        self.debug_message(f"POST : {self.crud.model.__name__} < {data}")
        return self.REQUEST(uid=0, data=data, format=format)

    @BaseAPI.include_parsed_request
    def PUT(self, data, format, uid):
        self.debug_message(f"PUT : {self.crud.model.__name__}:{uid} < {data}")
        return self.REQUEST(uid=int(uid), data=data, format=format)

    @BaseAPI.include_parsed_request
    def DELETE(self, _data, _format, uid):
        self.debug_message(f"DELETE : {self.crud.model.__name__}:{uid}")
        return self.REQUEST(uid=-int(uid), data={}, format={})
