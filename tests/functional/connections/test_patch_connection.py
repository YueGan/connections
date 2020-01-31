from http import HTTPStatus

import pytest
from tests.factories import PersonFactory, ConnectionFactory

from connections.models.connection import Connection


@pytest.fixture
def connection_payload():
    return {
        'connection_type': 'mother',
    }


def test_can_patch_connection(db, testapp, connection_payload):
    connection = ConnectionFactory()
    db.session.commit()

    connection_id = connection.id
    res = testapp.patch(f"connections/{connection_id}", json=connection_payload)

    assert res.status_code == HTTPStatus.OK

    assert 'id' in res.json

    connection = Connection.query.get(res.json['id'])

    assert connection is not None
    assert connection.connection_type.value == connection_payload['connection_type']


@pytest.mark.parametrize('field, value, error_message', [
    pytest.param('connection_type', None, 'Field may not be null.', id='missing from personn id'),
    pytest.param('connection_type', 'not_friend', "Invalid value.", id='invalid connection type',
                 # marks=pytest.mark.xfail
                 ),
])
def test_create_connection_validate(db, testapp, connection_payload, field, value, error_message):
    connection_payload[field] = value
    connection = ConnectionFactory()

    res = testapp.patch(f'/connections/{connection.id}', json=connection_payload)
    assert res.status_code == HTTPStatus.BAD_REQUEST
    assert res.json['description'] == 'Input failed validation.'
    errors = res.json['errors']
    assert error_message in errors[field][0]
