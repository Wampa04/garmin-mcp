#!/usr/bin/env python3
"""Generate Garmin Connect (garth) session tokens locally.

Run this once on your own machine. It logs in to Garmin with your
email/password (handling MFA interactively) and writes the resulting
session tokens to a `tokens/` directory. Copy that directory to your VPS
and mount it into the container (see README); the server then authenticates
with these tokens and never needs your password.

Usage:
    python scripts/generate_tokens.py
"""

from __future__ import annotations

import getpass
import os
import sys

from garminconnect import Garmin

# Write tokens to <repo-root>/tokens regardless of where the script is run from.
TOKENSTORE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tokens"
)


def main() -> int:
    print("Garmin Connect login — generate session tokens")
    print(f"Tokens will be written to: {TOKENSTORE}\n")

    email = input("Garmin email: ").strip()
    password = getpass.getpass("Garmin password: ")

    client = Garmin(
        email=email,
        password=password,
        prompt_mfa=lambda: input("MFA code (if prompted): ").strip(),
    )

    # The directory must exist before login: garminconnect persists the
    # tokens by calling client.dump(tokenstore) and silently swallows any
    # error, so a missing directory would mean no tokens are written.
    os.makedirs(TOKENSTORE, exist_ok=True)

    try:
        # Passing the tokenstore makes login() persist the session tokens
        # to that directory after a successful credential login.
        client.login(TOKENSTORE)
    except Exception as exc:  # noqa: BLE001
        print(f"\nLogin failed: {exc}", file=sys.stderr)
        return 1

    if not os.listdir(TOKENSTORE):
        print(
            "\nLogin reported success but no token files were written to "
            f"{TOKENSTORE}.",
            file=sys.stderr,
        )
        return 1

    print(f"\nSuccess. Tokens saved to {TOKENSTORE}")
    print("Next: copy this directory to your server and mount it at /tokens.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
