from flask import Flask, jsonify
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema.exceptions import SchemaError

user_schema = {
    "type":"object",
    "properties":{
        "name": {
            "type":"string",
        },
        "username": {
            "type":"string",
        },
        "email": {
            "type":"string",
            "format":"email"
        },
        "password": {
            "type":"string",
            "minLength": 5
        },
        "location": {
            "type":"integer",
            "minLength":5
        }
    },
    "required": ["email", "password", "location", "username"],
    "additionalProperties":False
}

def validate_user(data):
    try:
        validate(data, user_schema)
    except ValidationError as error:
        return {'ok': False, 'message':error}
    except SchemaError as error:
        return {'ok': False, 'message':error}
    return {'ok':True, 'data':data}

