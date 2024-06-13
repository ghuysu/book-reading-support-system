from mongoengine import Document, StringField, ListField

class Account(Document):
    username = StringField(required=False)
    password = StringField(required=False)
    role = StringField(default="user")
    meta = {
        'collection': 'Accounts'
    }
    def to_dict(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "role": self.role
        }