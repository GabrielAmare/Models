import json
from flask import request, jsonify
from flask_login import current_user
from .BaseModel import RequestMode


class API:
    def __init__(self, model):
        self.model = model

    @staticmethod
    def response(status, data=None, message=None):
        try:
            return jsonify(dict(status=status, data=data, message=message))
        except Exception as e:
            return jsonify(dict(status="error", data=None, message=str(e)))

    @staticmethod
    def success(data):
        return API.response(status="success", data=data)

    @staticmethod
    def error(message):
        return API.response(status="error", message=message)

    @staticmethod
    def parse_request():
        try:
            request_data = json.loads(request.data, encoding="utf-8")
            data = request_data.get('data', {})
            format = request_data.get('format', {})
            return data, format
        except:
            return dict(request.form), {}

    def build_routes(self, api):
        name = self.model.__name__.lower()

        api.add_url_rule(
            rule='/json/' + name + '/new',
            endpoint='POST_' + name,
            view_func=lambda: self.POST(),
            methods=['POST']
        )
        api.add_url_rule(
            rule='/json/' + name + '/<uid>',
            endpoint='GET_' + name,
            view_func=lambda uid: self.GET(int(uid)),
            methods=['GET']
        )
        api.add_url_rule(
            rule='/json/' + name + '/<uid>',
            endpoint='PUT_' + name,
            view_func=lambda uid: self.PUT(int(uid)),
            methods=['PUT']
        )
        api.add_url_rule(
            rule='/json/' + name + '/<uid>',
            endpoint='DELETE_' + name,
            view_func=lambda uid: self.DELETE(int(uid)),
            methods=['DELETE']
        )

    def GET(self, uid, mode=RequestMode.EAGER):
        data, format = self.parse_request()

        if self.model.debug:
            print(f"GET : {self.model.__name__}:{uid}")

        client_data = self.model.__crud__.apply_client(
            user=current_user,
            uid=uid,
            data={},
            format=format,
            mode=mode
        )
        return self.success(client_data)

    def POST(self, mode=RequestMode.EAGER):
        data, format = self.parse_request()

        if self.model.debug:
            print(f"POST : {self.model.__name__} < {data}")

        client_data = self.model.__crud__.apply_client(
            user=current_user,
            uid=0,
            data=data,
            format=format,
            mode=mode
        )
        return self.success(client_data)

    def PUT(self, uid, mode=RequestMode.EAGER):
        data, format = self.parse_request()

        if self.model.debug:
            print(f"PUT : {self.model.__name__}:{uid} < {data}")

        client_data = self.model.__crud__.apply_client(
            user=current_user,
            uid=uid,
            data=data,
            format=format,
            mode=mode
        )
        return self.success(client_data)

    def DELETE(self, uid, mode=RequestMode.EAGER):
        if self.model.debug:
            print(f"DELETE : {self.model.__name__}:{uid}")

        client_data = self.model.__crud__.apply_client(
            user=current_user,
            uid=-uid,
            data={},
            format={},
            mode=mode
        )
        return self.success(client_data)
