from datetime import datetime, UTC

import pytest
from freezegun import freeze_time

from salary_tracker.domain.auth.models import AuthProviderUserData, AuthProvider
from salary_tracker.domain.auth.impl.provider import GoogleAuthProviderUserDataExtractor


@pytest.fixture
def id_token():
    return "eyJhbGciOiJSUzI1NiIsImtpZCI6ImIyNjIwZDVlN2YxMzJiNTJhZmU4ODc1Y2RmMzc3NmMwNjQyNDlkMDQiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI0MDc0MDg3MTgxOTIuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI0MDc0MDg3MTgxOTIuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDQ3MzM0MjMwMTAyMjg2MTc1OTciLCJlbWFpbCI6Inh4aXhpZGl4eEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6Ikp6cmJMZzktTGh1MEhsYW4xTlVaVGciLCJuYW1lIjoiSXhpZGkgSXhpZGkiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jTFhmTklsMmlQTW1TbUN5NFBHdzBheDZJcjE1dXNnaW9kSWFSMERYa1N6YlRCYmxRPXM5Ni1jIiwiZ2l2ZW5fbmFtZSI6Ikl4aWRpIiwiZmFtaWx5X25hbWUiOiJJeGlkaSIsImlhdCI6MTcyNzA5ODIxOCwiZXhwIjoxNzI3MTAxODE4fQ.hlSvtd9a9Nb4-BTB18UGSczzs0z2ESNzZPfMXX9hDSRNZV4bu90X_jKeafRZlJ4Z_ZHDjZgNB6FdjNRMJ14nQ9BhdETRdas9BLmGKVPiYXh4oHIwwCNSjzd8WtHjsCCgceh7udnRh72Z-FpAA9GeSTRWbDSj_UBSKObraJ9QhLX5HVLzWqtUVHmDZHU9TjKo8wZG6oZTFREUHCKgn67DuMfn1GZ5ymR2iRbnhJe2qrUEUBJ4kShen4SNmBmmcizWQdoJyGLPZFlJ1i82QBow7jXX-vkv5CyDsr3PPrxEmWlNwYy086LEf_Rf9P1LfBFMeuCEjb7VsF0HGtWx-u826g"

@pytest.fixture
def app_client_id():
    return "407408718192.apps.googleusercontent.com"

@pytest.fixture
def extractor(app_client_id):
    return GoogleAuthProviderUserDataExtractor(app_client_id=app_client_id)

@freeze_time(datetime(2024, 9, 23, 13, 35, tzinfo=UTC))
async def test_extract_from_token(extractor, id_token):
    expected = AuthProviderUserData(
        provider=AuthProvider.GOOGLE,
        email="xxixidixx@gmail.com",
        external_id="104733423010228617597",
        name="Ixidi Ixidi",
        avatar="https://lh3.googleusercontent.com/a/ACg8ocLXfNIl2iPMmSmCy4PGw0ax6Ir15usgiodIaR0DXkSzbTBblQ=s96-c"
    )

    result = await extractor.extract_from_token(id_token)

    assert result == expected

async def test_extract_from_token_invalid_token(extractor):
    result = await extractor.extract_from_token("invalid")

    assert result is None

async def test_extract_from_token_invalid_audience(id_token):
    extractor = GoogleAuthProviderUserDataExtractor(app_client_id="invalid")

    result = await extractor.extract_from_token(id_token)

    assert result is None

@freeze_time(datetime(2024, 9, 23, 15, 35, tzinfo=UTC))
async def test_extract_from_token_expired(extractor, id_token):
    result = await extractor.extract_from_token(id_token)

    assert result is None

