import pytest
from urllib.parse import urlparse
from flask import session, g


def test_login(client, auth):
    assert client.get("/login").status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/index"
    auth.logout()

    response = auth.login(username="rmontanana", password="patito")
    assert response.headers["Location"] == "/index"

    with client:
        client.get("/index")
        assert session["_user_id"] == "1"
        assert g._login_user.username == "rmontanana"
        auth.logout()


def test_login_invalid(client, auth):
    response = auth.login(
        username="rmontanana", password="patato", follow_redirects=True
    )
    assert b"Invalid username or password" in response.data
    assert response.status_code == 200


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
