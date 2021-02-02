from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from app.basemodels import db, CRUD_MixIn


class Roles(db.Model, CRUD_MixIn):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(250), nullable=True, unique=True)
    description = db.Column(db.String(250))

    def __init__(self,  name, ):

        self.name = name


class RolesSchema(Schema):

    not_blank = validate.Length(min=1, error='Field cannot be blank')
    # add validate=not_blank in required fields
    id = fields.Integer(dump_only=True)

    name = fields.String(validate=not_blank)

    # self links
    def get_top_level_links(self, data, many):
        if many:
            self_link = "/roles/"
        else:
            self_link = "/roles/{}".format(data['id'])
        return {'self': self_link}

    class Meta:
        type_ = 'roles'
