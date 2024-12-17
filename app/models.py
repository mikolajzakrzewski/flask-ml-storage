from app.db import db


class DataPoint(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    feature_1 = db.mapped_column(db.Float, nullable=False)
    feature_2 = db.mapped_column(db.Float, nullable=False)
    category = db.mapped_column(db.Integer, nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def __repr__(self):
        return f"DataPoint({self.id}, {self.feature_1}, {self.feature_2}, {self.category})"
