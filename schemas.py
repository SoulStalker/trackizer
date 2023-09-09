from marshmallow import Schema, validate, fields


class TaskSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=[validate.Length(max=100)])
    description = fields.String(required=True, validate=[validate.Length(max=500)])
    start_time = fields.Time(required=False)
    end_time = fields.Time(required=False)
    completed = fields.Boolean(default=False)
    message = fields.String(dump_only=True)


class UserSchema(Schema):
    name = fields.String(required=True, validate=[
        validate.Length(max=250)])
    email = fields.String(required=True, validate=[
        validate.Length(max=250)])
    password = fields.String(required=True, validate=[
        validate.Length(max=100)], load_only=True)
    tasks = fields.Nested(TaskSchema, many=True, dump_only=True)


class AuthSchema(Schema):
    access_token = fields.String(dump_only=True)
    message = fields.String(dump_only=True)
