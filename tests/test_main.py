from flask import url_for, g
from beflask import app


# def test_config_init():
#     assert not app.create_app()[1].testing
#     assert app.create_app("testing")[1].testing


def test_index(client):
    response = client.get("/")
    # check image is in the response
    assert b"img/robert-lukeman-_RBcxo9AU-U-unsplash.jpg" in response.data


def test_index_logged(client, auth):
    assert auth.login(follow_redirects=True).status_code == 200
    with client:
        response = client.get("/")
        assert (
            b"img/robert-lukeman-_RBcxo9AU-U-unsplash.jpg" not in response.data
        )
        assert (
            b"Experiments with local discretization and Bayesian"
            in response.data
        )
        assert b"discretizbench" in response.data
    auth.logout()


def test_set_benchmark_guest(client, auth, app):
    assert auth.login(follow_redirects=True).status_code == 200
    with app[1].test_request_context():
        url = url_for("main.set_benchmark", benchmark_id=1)
        with client:
            response = client.get(url, follow_redirects=True)
            assert response.status_code == 200
            assert g._login_user.benchmark_id == 1
            assert b"Benchmark already selected." in response.data
            response = client.get("/set_benchmark/2", follow_redirects=True)
            assert g._login_user.benchmark_id == 1
            assert b"discretizbench" in response.data
            assert b"You are not an admin." in response.data
            auth.logout


def test_set_benchmark_admin(client, auth, app, admin_user, admin_password):
    assert (
        auth.login(
            username=admin_user, password=admin_password, follow_redirects=True
        ).status_code
        == 200
    )
    with app[1].test_request_context():
        url = url_for("main.set_benchmark", benchmark_id=1)
        with client:
            response = client.get(url, follow_redirects=True)
            assert response.status_code == 200
            assert g._login_user.benchmark_id == 1
            assert b"Benchmark already selected." in response.data
            response = client.get("/set_benchmark/2", follow_redirects=True)
            assert g._login_user.benchmark_id == 2
            assert b"odtebench" in response.data
            assert (
                b"Experiments with STree and Ensemble classifiers"
                in response.data
            )
            response = client.get("/set_benchmark/31", follow_redirects=True)
            assert g._login_user.benchmark_id == 2
            assert b"odtebench" in response.data
            assert (
                b"Experiments with STree and Ensemble classifiers"
                in response.data
            )
            assert b"Benchmark not found." in response.data
            auth.logout


def test_config(app, client, auth):
    explanations = {
        "score": "Deafult score if none is provided",
        "platform": "Name of the platform running benchmarks",
        "model": "Default model used if none is provided",
        "stratified": "Wether or not to split data in a stratified way",
        "source_data": "Type of datasets",
        "discretize": "Discretize of not datasets before training",
        "fit_features": "Wheter or not to include features names in fit",
        "seeds": "Seeds used to train/test models",
        "nodes": "Label for nodes in report",
        "leaves": "Label for leaves in report",
        "depth": "Label for depth in report",
        "margin": "Margin to add to ZeroR classifier in binary classes "
        "datasets",
        "framework": "HTML Framework default used in be_flask command",
    }
    assert auth.login(follow_redirects=True).status_code == 200
    with app[1].test_request_context():
        url = url_for("main.config")
        with client:
            response = client.get(url)
            assert response.status_code == 200
            for key, value in explanations.items():
                assert bytes(key, "utf-8") in response.data
                assert bytes(value, "utf-8") in response.data
