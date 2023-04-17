from app import db


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f""
