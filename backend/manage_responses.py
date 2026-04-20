"""
Script for managing survey responses.

Usage:
    python3 manage_responses.py count              # Count responses
    python3 manage_responses.py clear              # Delete all responses (with confirmation)
"""

import sys
import logging

from database import engine, Base
from sqlalchemy import text
from sqlalchemy.orm import Session
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger("manage_responses")


def count_responses():
    with engine.connect() as conn:
        count = conn.execute(text('SELECT COUNT(*) FROM responses')).scalar()
        print(f"Total responses: {count}")


def clear_responses():
    with engine.connect() as conn:
        count = conn.execute(text('SELECT COUNT(*) FROM responses')).scalar()

        if count == 0:
            print("No responses to delete.")
            return

        print(f"This will permanently delete {count} response(s).")
        confirm = input("Are you sure? Type 'yes' to confirm: ")

        if confirm.lower() != "yes":
            print("Operation cancelled.")
            return

        conn.execute(text('DELETE FROM responses'))
        conn.commit()
        logger.info(f"All responses deleted: {count} row(s) removed")
        print(f"Done. {count} response(s) deleted.")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "count":
        count_responses()
    elif command == "clear":
        clear_responses()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
