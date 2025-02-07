from app import db


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'title': self.title,
            'artist': self.artist
        }
