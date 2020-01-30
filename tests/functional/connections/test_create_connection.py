from http import HTTPStatus

import pytest
from tests.factories import PersonFactory

from connections.models.connection import Connection


@pytest.fixture
def connection_payload():
    return {
        'from_person_id': 1,
        'to_person_id': 2,
        'connection_type': 'friend',
    }


def test_can_create_connection(db, testapp):
    person_from = PersonFactory(first_name='Diana')
    person_to = PersonFactory(first_name='Harry')
    db.session.commit()
    payload = {
        'from_person_id': person_from.id,
        'to_person_id': person_to.id,
        'connection_type': 'mother',
    }
    res = testapp.post('/connections', json=payload)

    assert res.status_code == HTTPStatus.CREATED

    assert 'id' in res.json

    connection = Connection.query.get(res.json['id'])

    assert connection is not None
    assert connection.from_person_id == person_from.id
    assert connection.to_person_id == person_to.id
    assert connection.connection_type.value == 'mother'


@pytest.mark.parametrize('field, value, error_message', [
    pytest.param('from_person_id', None, 'Field may not be null.', id='missing from personn id'),
    pytest.param('to_person_id', None, 'Field may not be null.', id='missing to person id'),
    pytest.param('from_person_id', "String", 'Not a valid integer.',
                 id='missing from personn id'),
    pytest.param('to_person_id', "String", 'Not a valid integer.', id='missing to person id'),
    pytest.param('connection_type', 'not_friend', 'Invalid enum member not_friend', id='invalid connection type',
                 # marks=pytest.mark.xfail
                 ),
])
def test_create_connection_validate(db, testapp, connection_payload, field, value, error_message):
    connection_payload[field] = value

    res = testapp.post('/connections', json=connection_payload)
    assert res.status_code == HTTPStatus.BAD_REQUEST
    assert res.json['description'] == 'Input failed validation.'
    errors = res.json['errors']
    assert error_message in errors[field]
