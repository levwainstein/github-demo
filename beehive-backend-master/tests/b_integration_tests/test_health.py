def test_health_endpoints(app):
    # liveness probe endpoint should return 200
    res = app.test_client().get('api/inner/v1/health/livez')
    assert res.status_code == 200

    # readiness probe endpoint should return 200
    res = app.test_client().get('api/inner/v1/health/readyz')
    assert res.status_code == 200
