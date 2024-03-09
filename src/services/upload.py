import secrets
import string


def sha():
    sha = ""
    for _ in range(6):
        x = secrets.randbelow(2)
        if x == 0:
            sha += str(secrets.randbelow(10))
        else:
            sha += secrets.choice(string.ascii_lowercase)

    return sha
