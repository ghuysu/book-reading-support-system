from mongoengine import Document, StringField, ListField, DateTimeField

class File(Document):
    user = StringField(required=True)
    img_urls = ListField(StringField())
    predictions = ListField(StringField())
    date = DateTimeField()
    file_name = StringField()
    meta = {
        'collection': 'Files'
    }
    def to_dict(self):
        return {
            "id": str(self.id),
            "image_urls": self.img_urls,
            "predictions": self.predictions,
            "date": self.date,
            "file_name": self.file_name
        }
