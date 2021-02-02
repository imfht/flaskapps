from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from app.basemodels import db, CRUD_MixIn
from datetime import datetime



class {Resources}(db.Model, CRUD_MixIn):
    id = db.Column(db.Integer, primary_key=True)
    {db_rows}

    def __init__(self, {init_args}):
        {init_self_vars}


class {Resources}Schema(Schema):

    not_blank = validate.Length(min=1, error='Field cannot be blank')
    #add validate=not_blank in required fields
    id = fields.Integer(dump_only=True)
    {schema}
    
    #self links    
    def get_top_level_links(self, data, many):
        if many:
            self_link = "/{resources}/"
        else:
            self_link = "/{resources}/{{}}".format(data['id'])
        return {{'self': self_link}}

    class Meta:
        type_ = '{resources}'
