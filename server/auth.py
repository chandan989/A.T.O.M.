# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""
API Key authentication module for ATOM server.
Generates a secure API key on boot and validates incoming requests.
"""

import os
import secrets
from fastapi import Header, HTTPException, status

# Generate API key on module import (server boot)
# Can be overridden via ATOM_API_KEY environment variable
_API_KEY = os.environ.get("ATOM_API_KEY", secrets.token_hex(32))

def get_api_key() -> str:
    """Returns the current API key."""
    return _API_KEY

def verify_api_key(authorization: str = Header(None)) -> str:
    """
    FastAPI dependency that verifies the Authorization header.
    Expects: Authorization: Bearer <api_key>
    """
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header. Use: Authorization: Bearer <api_key>"
        )

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Use: Authorization: Bearer <api_key>"
        )

    token = parts[1]
    if not secrets.compare_digest(token, _API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return token

def print_api_key_banner():
    """Prints the API key in a visible banner on server startup."""
    print("\n" + "=" * 60)
    print("  A.T.O.M. SERVER — API KEY")
    print("=" * 60)
    print(f"  {_API_KEY}")
    print("=" * 60)
    print("  Use this key to connect from the frontend.")
    print("  Header: Authorization: Bearer <key>")
    print("=" * 60 + "\n")
