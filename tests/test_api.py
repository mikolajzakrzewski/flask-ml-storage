def test_get_api_data(client):
    response = client.get('/api/data')
    assert response.status_code == 200
    assert response.json == []

    for _ in range(10):
        response = client.post('/api/data', json={
            'feature_1': 5.0,
            'feature_2': 6.0,
            'category': 1
        })
        assert response.status_code == 201

    response = client.get('/api/data')
    assert response.status_code == 200
    assert len(response.json) == 10
    assert all(['id' in record for record in response.json])
    assert all(['feature_1' in record for record in response.json])
    assert all(['feature_2' in record for record in response.json])
    assert all(['category' in record for record in response.json])


def test_post_api_data(client):
    response = client.post('/api/data', json={
        'feature_1': 5.0,
        'feature_2': 6.0,
        'category': 1
    })
    assert response.status_code == 201
    assert response.json['id']

    response = client.post('/api/data', json={})
    assert response.status_code == 400


def test_delete_api_data(client):
    response = client.post('/api/data', json={
        'feature_1': 5.0,
        'feature_2': 6.0,
        'category': 1
    })
    record_id = response.json['id']

    response = client.delete(f'/api/data/{record_id}')
    assert response.status_code == 200

    response = client.get('/api/data')
    assert response.status_code == 200
    assert response.json == []

    response = client.delete(f'/api/data/{record_id}')
    assert response.status_code == 404


def test_api_prediction(client):
    response = client.get('/api/predictions')
    assert response.status_code == 400

    response = client.get('/api/predictions?feature_1=5.0&feature_2=6.0')
    assert response.status_code == 409

    test_data_point = {
        'feature_1': 5.0,
        'feature_2': 6.0,
        'category': 1
    }

    for _ in range(10):
        response = client.post('/api/data', json=test_data_point)
        assert response.status_code == 201

    response = client.get('/api/predictions?feature_1=5.0&feature_2=6.0')
    assert response.status_code == 200
    assert response.json['category']
