from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

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


def predict_category_by_features(feature_1, feature_2):
    n_neighbors = 3
    data_points = db.session.scalars(db.select(DataPoint)).all()
    if len(data_points) < n_neighbors:
        return None

    x = [[data_point.feature_1, data_point.feature_2] for data_point in data_points]
    y = [data_point.category for data_point in data_points]

    scaler = StandardScaler()
    standardized_x = scaler.fit_transform(x)
    standardized_features = scaler.transform([[feature_1, feature_2]])

    neigh = KNeighborsClassifier(n_neighbors=n_neighbors)
    neigh.fit(standardized_x, y)
    return neigh.predict(standardized_features)[0]


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
            return render_template("error.html", error_code='400 Bad Request',
                                   error_message='The form failed validation.'), 400

        db.session.add(DataPoint(feature_1=feature_1, feature_2=feature_2, category=category))
        db.session.commit()
        return redirect(url_for('home'))

    else:
        return render_template("add_record.html")


@app.route('/delete/<int:record_id>', methods=['POST'])
def delete(record_id):
    data_point = db.session.scalar(db.select(DataPoint).where(DataPoint.id == record_id))
    if data_point is None:
        return render_template("error.html", error_code='404 Not Found',
                               error_message=f'Record with ID {record_id} is not present in the database.'), 404

    else:
        db.session.delete(data_point)
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            feature_1 = float(request.form['feature_1'])
            feature_2 = float(request.form['feature_2'])

        except ValueError:
            return render_template("error.html", error_code='400 Bad Request',
                                   error_message='The form failed validation.'), 400

        predicted_category = predict_category_by_features(feature_1, feature_2)
        if predicted_category is None:
            return render_template("error.html", error_code='409 Conflict',
                                   error_message='Not enough records in the database to make a prediction.'), 409

        return render_template("predicted_category.html", predicted_category=predicted_category)

    else:
        return render_template("predict_category.html")


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


@app.route('/api/predictions')
def api_predictions():
    try:
        feature_1 = float(request.args['feature_1'])
        feature_2 = float(request.args['feature_2'])

    except (KeyError, ValueError):
        return jsonify({'error': 'Invalid data'}), 400

    predicted_category = predict_category_by_features(feature_1, feature_2)
    if predicted_category is None:
        return jsonify({'error': 'Not enough records in the database to make a prediction.'}), 409

    return jsonify({'category': int(predicted_category)})


if __name__ == '__main__':
    app.run()
