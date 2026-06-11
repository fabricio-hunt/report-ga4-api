"""Extract refresh token from local token.pickle for Databricks Secrets setup."""

from __future__ import annotations

import pickle
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOKEN_FILE = PROJECT_ROOT / "token.pickle"


def main() -> int:
    if not TOKEN_FILE.exists():
        print(f"Arquivo não encontrado: {TOKEN_FILE}")
        print("Execute um job localmente primeiro para gerar o token OAuth.")
        return 1

    with open(TOKEN_FILE, "rb") as f:
        creds = pickle.load(f)

    if not creds.refresh_token:
        print("Refresh token não encontrado no token.pickle.")
        return 1

    print("Refresh token (copie para o Databricks Secret 'refresh_token'):\n")
    print(creds.refresh_token)
    return 0


if __name__ == "__main__":
    sys.exit(main())
