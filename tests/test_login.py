from flask import session, g, url_for


def test_login(app, client, auth, admin_user, admin_password):
    with app[1].test_request_context():
        url_login = url_for("main.login")
        url_index = url_for("main.index")

    assert client.get(url_login).status_code == 200
    response = auth.login()
    assert response.headers["Location"] == url_index
    auth.logout()

    response = auth.login(username=admin_user, password=admin_password)
    assert response.headers["Location"] == url_index
    with client:
        client.get(url_index)
        assert session["_user_id"] == "1"
        assert g._login_user.username == admin_user
        # Check if an already logged in user is redirected to index
        assert client.get(url_login).status_code == 302
        response = client.get(url_login)
        assert response.status_code == 302
        assert response.headers["Location"] == url_index
        auth.logout()


def test_login_invalid(auth, admin_user):
    response = auth.login(
        username=admin_user, password="wrong_password", follow_redirects=True
    )
    assert b"Invalid username or password" in response.data
    assert response.status_code == 200


def test_access_page_not_logged(client, app, auth, guest_user, guest_password):
    with app[1].test_request_context():
        url_login = url_for("main.login")
        url_config = url_for("main.config")
    # Check if a not logged in user is redirected to login with next param
    response = client.get(url_config)
    header_login = f"{url_login}?next=%2Fconfig"
    assert response.headers["Location"] == header_login
    assert response.status_code == 302
    # Check if a not logged in user is redirected to login
    response = client.get("/config", follow_redirects=True)
    assert b"Please log in to access this page." in response.data
    assert response.status_code == 200
    with client:
        data = {"username": guest_user, "password": guest_password}
        response = client.post(header_login, data=data, follow_redirects=True)
        assert response.status_code == 200
        responses = {
            "score": "Deafult score if none is provided",
            "platform": "Name of the platform running benchmarks",
            "model": "Default model used if none is provided",
        }
        for key, value in responses.items():
            assert bytes(key, "utf-8") in response.data
            assert bytes(value, "utf-8") in response.data


def test_logout_logged(client, auth):
    response = auth.login()
    with client:
        auth.logout()
        assert "user_id" not in session
        assert response.headers["Location"] == url_for("main.index")


def test_logout_not_logged(client, auth):
    with client:
        response = auth.logout()
        assert response.status_code == 302
        assert "user_id" not in session
        assert response.headers["Location"] == url_for("main.index")
        response = auth.logout(follow_redirects=True)
        assert b"You are not logged in." in response.data
