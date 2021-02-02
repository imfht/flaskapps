from flask import Blueprint, request, jsonify, make_response
from app.users.models import Users, UsersSchema
from flask_restful import Api
from app.baseviews import Resource, parse_token
from app.basemodels import db
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from werkzeug.security import check_password_hash, generate_password_hash


users = Blueprint('users', __name__)
# http://marshmallow.readthedocs.org/en/latest/quickstart.html#declaring-schemas
# https://github.com/marshmallow-code/marshmallow-jsonapi
schema = UsersSchema(strict=True)
api = Api(users)

# Users


class CreateListUsers(Resource):
    """http://jsonapi.org/format/#fetching
    A server MUST respond to a successful request to fetch an individual resource or resource collection with a 200 OK response.
    A server MUST respond with 404 Not Found when processing a request to fetch a single resource that does not exist, except when the request warrants a 200 OK response with null as the primary data (as described above)
    a self link as part of the top-level links object"""

    def get(self):
        users_query = Users.query.all()
        results = schema.dump(users_query, many=True).data
        return results
    
    """A resource can be created by sending a POST request to a URL that represents a collection of users. The request MUST include a single resource object as primary data. The resource object MUST contain at least a type member.
    If a POST request did not include a Client-Generated ID and the requested resource has been created successfully, 
    the server MUST return a 201 Created status code"""
    
    def post(self):
        raw_dict = request.get_json(force=True)
        try:
            schema.validate(raw_dict)
            request_dict = raw_dict['data']['attributes']
            payload = parse_token(request)
            logged_user = Users.query.get(payload['sub'])
            createdby = logged_user.name
            updatedby = logged_user.name
            password = generate_password_hash (request_dict['password'] )

           
            user = Users(
                         request_dict['email'],
                         password,
                         request_dict['name'],
                         createdby,
                         updatedby ,

                         )
            user.add(user)
            # Should not return password hash
            query = Users.query.get(user.id)
            results = schema.dump(query).data
            return results, 201

        except ValidationError as err:
            resp = jsonify({"error": err.messages})
            resp.status_code = 403
            return resp

        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = 403
            return resp
     


class GetUpdateDeleteUser(Resource):

    """http://jsonapi.org/format/#fetching
    A server MUST respond to a successful request to fetch an individual resource or resource collection with a 200 OK response.
    A server MUST respond with 404 Not Found when processing a request to fetch a single resource that does not exist, except when the request warrants a 200 OK response with null as the primary data (as described above)
    a self link as part of the top-level links object"""

    def get(self, id):
        user_query = Users.query.get_or_404(id)
        result = schema.dump(user_query).data
        return result

    """http://jsonapi.org/format/#crud-updating"""

    def patch(self, id):
        user = Users.query.get_or_404(id)
        raw_dict = request.get_json(force=True)
        try:
            schema.validate(raw_dict)
            request_dict = raw_dict['data']['attributes']
            payload = parse_token(request)
            logged_user = Users.query.get(payload['sub'])
            request_dict['updatedby'] = logged_user.name

            for key, value in request_dict.items():
                if key == "password":
                    value = generate_password_hash(value)
                setattr(user, key, value)

            user.update()
            return self.get(id)

        except ValidationError as err:
            resp = jsonify({"error": err.messages})
            resp.status_code = 401
            return resp

        except SQLAlchemyError as e:
            db.session.rollback()

            resp = jsonify({"error": str(e.orig.args)})
            resp.status_code = 401
            return resp

    # http://jsonapi.org/format/#crud-deleting
    # A server MUST return a 204 No Content status code if a deletion request
    # is successful and no content is returned.
    def delete(self, id):
        user = Users.query.get_or_404(id)
        try:
            delete = user.delete(user)
            response = make_response()
            response.status_code = 204
            return response

        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e.orig.args)})
            resp.status_code = 401
            return resp


api.add_resource(CreateListUsers, '.json')
api.add_resource(GetUpdateDeleteUser, '/<int:id>.json')
