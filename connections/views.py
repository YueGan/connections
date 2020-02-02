from http import HTTPStatus

from flask import Blueprint
from webargs import fields
from webargs.flaskparser import use_args


from connections.models.connection import Connection, ConnectionType
from connections.models.person import Person
from connections.schemas import ConnectionSchema, PersonSchema

blueprint = Blueprint('connections', __name__)


@blueprint.route('/people', methods=['GET'])
@use_args({'sort': fields.Str(location='query')})
def get_people(args):
    people_schema = PersonSchema(many=True)

    order_query = None
    if(args):
        if(args['sort'] == '-created_at'):
            order_query = Person.created_at.desc()
        elif(args['sort'] == 'created_at'):
            order_query = Person.created_at
        elif(args['sort'] == '-first_name'):
            order_query = Person.first_name.desc()
        elif(args['sort'] == 'first_name'):
            order_query = Person.first_name
        elif(args['sort'] == '-last_name'):
            order_query = Person.last_name.desc()
        elif(args['sort'] == 'last_name'):
            order_query = Person.last_name

    people = Person.query.order_by(order_query).all()
    return people_schema.jsonify(people), HTTPStatus.OK


@blueprint.route('/people', methods=['POST'])
@use_args(PersonSchema(), locations=('json',))
def create_person(person):
    person.save()
    return PersonSchema().jsonify(person), HTTPStatus.CREATED


@blueprint.route('/connections', methods=['GET'])
def get_connections():
    connection_schema = ConnectionSchema(many=True)
    connections = Connection.query.all()

    return connection_schema.jsonify(connections), HTTPStatus.OK


@blueprint.route('/connections', methods=['POST'])
@use_args(ConnectionSchema(), locations=('json',))
def create_connection(connection):
    connection.save()
    return ConnectionSchema().jsonify(connection), HTTPStatus.CREATED


@blueprint.route('/connections/<connection_id>', methods=['PATCH'])
@use_args({
    'connection_type': fields.Str(
        location='json',
        validate=lambda x: x in ConnectionType._value2member_map_
    )})
def patch_connection(args, connection_id):
    Connection.query.get_or_404(connection_id)

    Connection.query.filter_by(id=connection_id).update(
        {'connection_type': args['connection_type']})

    return ConnectionSchema().jsonify(Connection.query.get(connection_id)), HTTPStatus.OK
