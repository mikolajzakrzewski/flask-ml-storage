from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data_points.db"
db = SQLAlchemy(app)


class DataPoint(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    feature_1 = db.mapped_column(db.Float, nullable=False)
    feature_2 = db.mapped_column(db.Float, nullable=False)
    category = db.mapped_column(db.Integer, nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def __repr__(self):
        return f"DataPoint({self.id}, {self.feature_1}, {self.feature_2}, {self.category})"


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    data_points = db.session.scalars(db.select(DataPoint))
    return render_template("home.html", data_points=data_points)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        try:
            feature_1 = float(request.form['feature_1'])
            feature_2 = float(request.form['feature_2'])
            category = int(request.form['category'])

        except ValueError:
            return render_template("add_record_error.html"), 400

        db.session.add(DataPoint(feature_1=feature_1, feature_2=feature_2, category=category))
        db.session.commit()
        return redirect(url_for('home'))

    else:
        return render_template("add_record.html")


@app.route('/delete/<int:record_id>', methods=['POST'])
def delete(record_id):
    data_point = db.session.scalar(db.select(DataPoint).where(DataPoint.id == record_id))
    if data_point is None:
        return render_template("delete_record_error.html", record_id=record_id), 404

    else:
        db.session.delete(data_point)
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/api/data', methods=['GET', 'POST'])
def api_data():
    if request.method == 'GET':
        data_points = db.session.scalars(db.select(DataPoint))
        return jsonify([data_point.to_dict() for data_point in data_points])

    elif request.method == 'POST':
        data = request.json
        try:
            data['feature_1'] = float(data['feature_1'])
            data['feature_2'] = float(data['feature_2'])
            data['category'] = int(data['category'])

        except (KeyError, ValueError):
            return jsonify({'error': 'Invalid data'}), 400

        data_point = DataPoint(feature_1=data['feature_1'], feature_2=data['feature_2'],
                               category=data['category'])
        db.session.add(data_point)
        db.session.commit()
        return jsonify({'id': data_point.id}), 201


@app.route('/api/data/<int:record_id>', methods=['DELETE'])
def api_delete(record_id):
    data_point = db.session.scalar(db.select(DataPoint).where(DataPoint.id == record_id))
    if data_point is None:
        return jsonify({'error': 'Record not found'}), 404

    else:
        db.session.delete(data_point)
        db.session.commit()
        return jsonify({'id': data_point.id})


if __name__ == '__main__':
    app.run()
