from connections.database import CreatedUpdatedMixin, CRUDMixin, db, Model
from connections.models.connection import ConnectionType


class Person(Model, CRUDMixin, CreatedUpdatedMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(145), unique=True, nullable=False)

    connections = db.relationship('Connection', foreign_keys='Connection.from_person_id')

    def get_connections(self, target, type):
        return [
            connection.to_person_id
            for connection in self.connections if connection.connection_type == type
            ]

    def mutual_friends(self, target):

        friend_id = self.get_connections(self, ConnectionType.friend)
        target_friend_id = self.get_connections(target, ConnectionType.friend)

        mutual_friends_id = list(set(friend_id) & set(target_friend_id))

        return db.session.query(Person).filter(Person.id.in_(mutual_friends_id)).all()
