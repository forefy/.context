#!/usr/bin/env python3
"""
Reusable Google Docs API auth helper.
Usage: from gdocs_auth import make_token, get_doc, do_batch
"""
import json, time, ssl, urllib.request, urllib.parse, base64

ssl_ctx = ssl._create_unverified_context()


def make_token(key_path: str) -> str:
    with open(key_path) as f:
        key_data = json.load(f)
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.backends import default_backend

    now = int(time.time())
    h = (
        base64.urlsafe_b64encode(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
        .rstrip(b"=")
        .decode()
    )
    p = (
        base64.urlsafe_b64encode(
            json.dumps(
                {
                    "iss": key_data["client_email"],
                    "scope": "https://www.googleapis.com/auth/drive",
                    "aud": "https://oauth2.googleapis.com/token",
                    "iat": now,
                    "exp": now + 3600,
                }
            ).encode()
        )
        .rstrip(b"=")
        .decode()
    )
    msg = f"{h}.{p}".encode()
    pk = serialization.load_pem_private_key(
        key_data["private_key"].encode(), password=None, backend=default_backend()
    )
    sig = (
        base64.urlsafe_b64encode(pk.sign(msg, padding.PKCS1v15(), hashes.SHA256()))
        .rstrip(b"=")
        .decode()
    )
    jwt = f"{h}.{p}.{sig}"
    data = urllib.parse.urlencode(
        {"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": jwt}
    ).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    return json.loads(urllib.request.urlopen(req, context=ssl_ctx).read())[
        "access_token"
    ]


def get_doc(doc_id: str, token: str) -> dict:
    req = urllib.request.Request(
        f"https://docs.googleapis.com/v1/documents/{doc_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    return json.loads(urllib.request.urlopen(req, context=ssl_ctx).read())


def do_batch(doc_id: str, token: str, ops: list, label: str = "") -> dict:
    """Apply a list of batchUpdate requests. Always sort ops high→low index before calling."""
    body = json.dumps({"requests": ops}).encode()
    req = urllib.request.Request(
        f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    resp = json.loads(urllib.request.urlopen(req, context=ssl_ctx).read())
    if label:
        print(f"  [{label}] -> OK ({len(ops)} ops)")
    return resp
