"""Drop-in `crypt` shim for Python 3.13+.

Python 3.13 removed the stdlib `crypt` module, but crawl's webtiles server
(`webserver/webtiles/userdb.py`) does `import crypt` and uses `crypt.crypt()`
for password hashing. `crypt-r` (the recommended replacement) has no wheel and
fails to build on Python 3.14, so this spike puts this shim on PYTHONPATH via
setup_webtiles.sh instead of patching crawl's source.

It reproduces the ONLY property userdb relies on:

    crypt(pw, crypt(pw, salt)) == crypt(pw, salt)

i.e. the stored hash can be fed back in as the salt and verifies. We do that by
echoing the salt "spec" (everything that identifies the salt) as the prefix of
the output, exactly like real crypt's `$algo$salt$hash` and 2-char DES formats.
This is NOT crypt(3)-compatible with existing system password databases — it is
only self-consistent, which is all the local spike server needs.
"""
import hashlib

METHOD_SHA512 = "6"
METHOD_SHA256 = "5"
METHOD_MD5 = "1"


def _salt_spec(salt):
    # "$algo$saltval$..."  -> spec "$algo$saltval$"   (drops any trailing hash)
    if salt.startswith("$"):
        parts = salt.split("$")
        if len(parts) >= 3:
            return "$" + parts[1] + "$" + parts[2] + "$"
    # traditional DES-style 2-char salt (or a hash whose first 2 chars are salt)
    return salt[:2]


def crypt(word, salt=None):
    if salt is None:
        salt = mksalt()
    spec = _salt_spec(salt)
    digest = hashlib.sha256((spec + word).encode("utf-8")).hexdigest()
    return spec + digest


def mksalt(method=None, *, rounds=None):
    import random
    chars = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    algo = method or METHOD_SHA512
    return "${}${}$".format(algo, "".join(random.choice(chars) for _ in range(8)))


if __name__ == "__main__":
    # self-check: the verification contract must hold for both salt formats
    for salt in ("$6$abcdEFGH$", "Xy"):
        stored = crypt("hunter2", salt)
        assert crypt("hunter2", stored) == stored, salt
        assert crypt("wrongpw", stored) != stored, salt
    print("crypt shim OK")
