async def test_me_returns_current_user(client, provide_logged_in_user):
    async with provide_logged_in_user() as user:
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 200
        assert response.json() == {
            "uuid": str(user.uuid),
            "email": user.email,
            "name": user.name
        }

async def test_me_not_logged_in(client):
    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401