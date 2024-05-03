import hashlib
from typing import Callable


def hash_file_all_algorithms(file_path: str):
    enabled_hash_algorithms: dict[str, Callable] = {
        "MD5sum": hashlib.md5,
        "SHA1": hashlib.sha1,
        "SHA256": hashlib.sha256
    }

    results_obj = {}
    for name, hash_obj in enabled_hash_algorithms.items():
        results_obj[name] = hash_obj()
    
    with open(file_path, "rb") as file:
        while True:
            data = file.read()
            if not data: break
            for hash_obj in results_obj.values():
                hash_obj.update(data)

    results: dict[str, str] = {}
    for name, hash_obj in results_obj.items():
        results[name] = hash_obj.hexdigest()

    return results