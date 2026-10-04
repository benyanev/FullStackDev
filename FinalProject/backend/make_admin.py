"""Make a user an admin (moderator) by email.

    python make_admin.py you@example.com                          # local
    docker compose exec backend python make_admin.py you@example.com   # Docker

The user must log out and back in to see the Admin link.
"""

import sys

from repositories.user_repository import get_user_by_email, set_user_role


def main():
    if len(sys.argv) != 2:
        print('Usage: python make_admin.py <email>')
        sys.exit(1)

    email = sys.argv[1].strip().lower()
    user = get_user_by_email(email)
    if user is None:
        print(f'No user with email {email}')
        sys.exit(1)

    set_user_role(user['id'], 'admin')
    print(f'{user["name"]} ({email}) is now an admin.')


if __name__ == '__main__':
    main()
