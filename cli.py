import argparse
import json
import sys

from user_management import (
    AccountStatus,
    AuthorizationError,
    NotFoundError,
    RegistrationService,
    Role,
    UserStore,
    ValidationError,
)


def print_json(value):
    print(json.dumps(value, indent=2, sort_keys=True))


def parse_args():
    parser = argparse.ArgumentParser(description="User management command-line interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    register = subparsers.add_parser("register", help="Register a new user")
    register.add_argument("--name", required=True)
    register.add_argument("--email", required=True)
    register.add_argument("--password", required=True)
    register.add_argument("--role", choices=[r.value for r in Role], default=Role.USER.value)
    register.add_argument("--organization-name")
    register.add_argument("--verification-docs", nargs="*", default=[])

    approve = subparsers.add_parser("approve-org", help="Approve organization verification")
    approve.add_argument("--admin-id", required=True)
    approve.add_argument("--user-id", required=True)

    reject = subparsers.add_parser("reject-org", help="Reject organization verification")
    reject.add_argument("--admin-id", required=True)
    reject.add_argument("--user-id", required=True)

    suspend = subparsers.add_parser("suspend", help="Suspend a user account")
    suspend.add_argument("--admin-id", required=True)
    suspend.add_argument("--user-id", required=True)

    remove = subparsers.add_parser("remove", help="Remove a user account")
    remove.add_argument("--admin-id", required=True)
    remove.add_argument("--user-id", required=True)

    update = subparsers.add_parser("update", help="Update an existing user account")
    update.add_argument("--user-id", required=True)
    update.add_argument("--name")
    update.add_argument("--email")
    update.add_argument("--password")

    auth = subparsers.add_parser("authenticate", help="Authenticate a user")
    auth.add_argument("--email", required=True)
    auth.add_argument("--password", required=True)

    list_users = subparsers.add_parser("list-users", help="List all users")
    list_users.add_argument("--role", choices=[r.value for r in Role], default=None)

    return parser.parse_args()


def main():
    args = parse_args()
    service = RegistrationService()

    try:
        if args.command == "register":
            account = service.register_user(
                {
                    "name": args.name,
                    "email": args.email,
                    "password": args.password,
                    "role": args.role,
                    "organization_name": args.organization_name,
                    "verification_docs": args.verification_docs,
                }
            )
            print_json(account.sanitize())

        elif args.command == "approve-org":
            account = service.approve_organization(args.admin_id, args.user_id)
            print_json(account.sanitize())

        elif args.command == "reject-org":
            account = service.reject_organization(args.admin_id, args.user_id)
            print_json(account.sanitize())

        elif args.command == "suspend":
            account = service.suspend_account(args.admin_id, args.user_id)
            print_json(account.sanitize())

        elif args.command == "remove":
            account = service.remove_account(args.admin_id, args.user_id)
            print_json(account.sanitize())

        elif args.command == "update":
            payload = {k: v for k, v in vars(args).items() if k in {"name", "email", "password"} and v}
            account = service.update_account(args.user_id, payload)
            print_json(account.sanitize())

        elif args.command == "authenticate":
            account = service.authenticate(args.email, args.password)
            print_json(account.sanitize())

        elif args.command == "list-users":
            users = service.store.list_users()
            if args.role:
                users = [u for u in users if u.role.value == args.role]
            print_json([u.sanitize() for u in users])

    except (ValidationError, AuthorizationError, NotFoundError) as error:
        print_json({"error": str(error)})
        sys.exit(1)


if __name__ == "__main__":
    main()
