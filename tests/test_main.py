from beflask import app


def test_config():
    assert not app.create_app()[1].testing
    assert app.create_app("testing")[1].testing


def test_index(client):
    response = client.get("/")
    # check image is in the response
    assert b"img/robert-lukeman-_RBcxo9AU-U-unsplash.jpg" in response.data
