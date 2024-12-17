from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from app.db import db
from app.models import DataPoint


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
