# stdlib
from typing import Dict

# third party
from fastapi import FastAPI
from httpx import AsyncClient


async def authenticate_user(
    app: FastAPI, client: AsyncClient, email: str, password: str
) -> Dict[str, str]:
    res = await client.post(app.url_path_for("login"), json={email, password})
    res = res.json()
    auth_token = res["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


async def authenticate_owner(app: FastAPI, client: AsyncClient) -> Dict[str, str]:
    return await authenticate_user(
        app, client, email="info@openmined.org", password="changethis"
    )
