import os

def get_repo_type() -> str:
    # default stays in-memory so nothing breaks
    return os.getenv("REPO_TYPE", "memory").lower()
