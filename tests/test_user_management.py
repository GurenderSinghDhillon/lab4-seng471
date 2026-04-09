import tempfile
import unittest
from pathlib import Path

from user_management import (
    AccountStatus,
    AuthorizationError,
    NotFoundError,
    RegistrationService,
    Role,
    UserStore,
    ValidationError,
)


class TestUserManagement(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store_path = Path(self.temp_dir.name) / "users.json"
        self.store = UserStore(path=self.store_path)
        self.service = RegistrationService(store=self.store)

        self.admin = self.service.register_user(
            {
                "name": "Admin User",
                "email": "admin@example.com",
                "password": "adminpass",
                "role": Role.ADMIN.value,
            }
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_register_standard_user(self):
        user = self.service.register_user(
            {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "password": "securepass",
                "role": Role.USER.value,
            }
        )
        self.assertEqual(user.role, Role.USER)
        self.assertEqual(user.account_status, AccountStatus.ACTIVE)
        self.assertEqual(user.verification_status.value, "not_required")

    def test_register_organization_requires_docs(self):
        with self.assertRaises(ValidationError):
            self.service.register_user(
                {
                    "name": "Org One",
                    "email": "org@example.com",
                    "password": "securepass",
                    "role": Role.ORGANIZATION.value,
                }
            )

    def test_register_organization_sets_pending(self):
        org = self.service.register_user(
            {
                "name": "Good Org",
                "email": "org@example.com",
                "password": "securepass",
                "role": Role.ORGANIZATION.value,
                "organization_name": "Good Org Ltd",
                "verification_docs": ["https://example.com/doc1.pdf"],
            }
        )
        self.assertEqual(org.role, Role.ORGANIZATION)
        self.assertEqual(org.verification_status.value, "pending")

    def test_admin_can_approve_organization(self):
        org = self.service.register_user(
            {
                "name": "Review Org",
                "email": "review@example.com",
                "password": "securepass",
                "role": Role.ORGANIZATION.value,
                "organization_name": "Review Org Ltd",
                "verification_docs": ["https://example.com/doc1.pdf"],
            }
        )

        approved = self.service.approve_organization(self.admin.user_id, org.user_id)
        self.assertEqual(approved.verification_status.value, "approved")

    def test_non_admin_cannot_approve(self):
        user = self.service.register_user(
            {
                "name": "Normal User",
                "email": "normal@example.com",
                "password": "securepass",
                "role": Role.USER.value,
            }
        )

        org = self.service.register_user(
            {
                "name": "Pending Org",
                "email": "pending@example.com",
                "password": "securepass",
                "role": Role.ORGANIZATION.value,
                "organization_name": "Pending Org Ltd",
                "verification_docs": ["https://example.com/doc1.pdf"],
            }
        )

        with self.assertRaises(AuthorizationError):
            self.service.approve_organization(user.user_id, org.user_id)

    def test_admin_can_suspend_and_remove(self):
        user = self.service.register_user(
            {
                "name": "Suspended User",
                "email": "suspend@example.com",
                "password": "securepass",
                "role": Role.USER.value,
            }
        )

        suspended = self.service.suspend_account(self.admin.user_id, user.user_id)
        self.assertEqual(suspended.account_status, AccountStatus.SUSPENDED)

        removed = self.service.remove_account(self.admin.user_id, user.user_id)
        self.assertEqual(removed.account_status, AccountStatus.REMOVED)

    def test_update_account_validations(self):
        user = self.service.register_user(
            {
                "name": "Update User",
                "email": "update@example.com",
                "password": "securepass",
                "role": Role.USER.value,
            }
        )

        updated = self.service.update_account(user.user_id, {"name": "Updated Name"})
        self.assertEqual(updated.name, "Updated Name")

        with self.assertRaises(ValidationError):
            self.service.update_account(user.user_id, {"password": "short"})

    def test_authenticate_rejects_suspended_account(self):
        user = self.service.register_user(
            {
                "name": "Auth User",
                "email": "auth@example.com",
                "password": "securepass",
                "role": Role.USER.value,
            }
        )
        self.service.suspend_account(self.admin.user_id, user.user_id)

        with self.assertRaises(AuthorizationError):
            self.service.authenticate(user.email, "securepass")

    def test_user_not_found_raises(self):
        with self.assertRaises(NotFoundError):
            self.service.approve_organization(self.admin.user_id, "missing-id")


if __name__ == "__main__":
    unittest.main()
