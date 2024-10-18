from datetime import datetime, UTC

import pytest
from freezegun import freeze_time

@pytest.mark.skip('Hard coded user in usecase')
@freeze_time(datetime(2024, 9, 23, 13, 35, tzinfo=UTC))
async def test_auth_provider_google_login(client):
    response = await client.post(
        "/api/v1/auth/auth-provider-login/google/",
        json={
            "external_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImIyNjIwZDVlN2YxMzJiNTJhZmU4ODc1Y2RmMzc3NmMwNjQyNDlkMDQiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI0MDc0MDg3MTgxOTIuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI0MDc0MDg3MTgxOTIuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDQ3MzM0MjMwMTAyMjg2MTc1OTciLCJlbWFpbCI6Inh4aXhpZGl4eEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6Ikp6cmJMZzktTGh1MEhsYW4xTlVaVGciLCJuYW1lIjoiSXhpZGkgSXhpZGkiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jTFhmTklsMmlQTW1TbUN5NFBHdzBheDZJcjE1dXNnaW9kSWFSMERYa1N6YlRCYmxRPXM5Ni1jIiwiZ2l2ZW5fbmFtZSI6Ikl4aWRpIiwiZmFtaWx5X25hbWUiOiJJeGlkaSIsImlhdCI6MTcyNzA5ODIxOCwiZXhwIjoxNzI3MTAxODE4fQ.hlSvtd9a9Nb4-BTB18UGSczzs0z2ESNzZPfMXX9hDSRNZV4bu90X_jKeafRZlJ4Z_ZHDjZgNB6FdjNRMJ14nQ9BhdETRdas9BLmGKVPiYXh4oHIwwCNSjzd8WtHjsCCgceh7udnRh72Z-FpAA9GeSTRWbDSj_UBSKObraJ9QhLX5HVLzWqtUVHmDZHU9TjKo8wZG6oZTFREUHCKgn67DuMfn1GZ5ymR2iRbnhJe2qrUEUBJ4kShen4SNmBmmcizWQdoJyGLPZFlJ1i82QBow7jXX-vkv5CyDsr3PPrxEmWlNwYy086LEf_Rf9P1LfBFMeuCEjb7VsF0HGtWx-u826g"
        })

    assert response.status_code == 200
    assert "set-cookie" in response.headers.keys()
    assert "refresh_token=" in response.headers["set-cookie"]


@pytest.mark.skip('Hard coded user in usecase')
@freeze_time(datetime(2024, 9, 23, 13, 35, tzinfo=UTC))
async def test_auth_provider_google_login_invalid_token(client):
    response = await client.post(
        "/api/v1/auth/auth-provider-login/google/",
        json={
            "external_token": "invalid"
        })

    assert response.status_code == 401
