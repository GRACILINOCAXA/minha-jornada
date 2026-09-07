import os


def test_module_exports_app_for_vercel():
    os.environ.setdefault('FLASK_ENV', 'production')
    import backend.app as app_module

    assert hasattr(app_module, 'app'), 'backend.app must export app for Vercel/serverless import'
    assert app_module.app is not None

    with app_module.app.test_client() as client:
        response = client.get('/api/health')
        assert response.status_code == 200, response.get_data(as_text=True)
