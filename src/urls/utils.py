import secrets
BASE62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def generate_short_code(length: int = 6) -> str:

    return "".join(
        secrets.choice(BASE62)
        for _ in range(length)
    )

