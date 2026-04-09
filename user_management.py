import hashlib
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_MIN_LENGTH = 8
USER_STORE_PATH = Path("data/users.json")


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _validate_email(email: str) -> None:
    if not EMAIL_REGEX.match(email):
        raise ValidationError("Invalid email address")


def _validate_password(password: str) -> None:
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValidationError(
            f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
        )


class Role(str, Enum):
    USER = "user"
    ORGANIZATION = "organization"
    ADMIN = "admin"


class VerificationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NOT_REQUIRED = "not_required"


class AccountStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REMOVED = "removed"


class UserManagementError(Exception):
    pass


class ValidationError(UserManagementError):
    pass


class AuthorizationError(UserManagementError):
    pass


class NotFoundError(UserManagementError):
    pass


@dataclass
class UserAccount:
    user_id: str
    name: str
    email: str
    role: Role
    password_hash: str
    organization_name: Optional[str] = None
    verification_docs: List[str] = field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.NOT_REQUIRED
    account_status: AccountStatus = AccountStatus.ACTIVE
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> Dict[str, object]:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "password_hash": self.password_hash,
            "organization_name": self.organization_name,
            "verification_docs": self.verification_docs,
            "verification_status": self.verification_status.value,
            "account_status": self.account_status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "UserAccount":
        return cls(
            user_id=data["user_id"],
            name=data["name"],
            email=data["email"],
            role=Role(data["role"]),
            password_hash=data["password_hash"],
            organization_name=data.get("organization_name"),
            verification_docs=list(data.get("verification_docs", [])),
            verification_status=VerificationStatus(data.get("verification_status", VerificationStatus.NOT_REQUIRED.value)),
            account_status=AccountStatus(data.get("account_status", AccountStatus.ACTIVE.value)),
            created_at=data.get("created_at", _now_iso()),
            updated_at=data.get("updated_at", _now_iso()),
        )

    def sanitize(self) -> Dict[str, object]:
        sanitized = self.to_dict()
        sanitized.pop("password_hash", None)
        return sanitized


class UserStore:
    def __init__(self, path: Path = USER_STORE_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _read(self) -> List[Dict[str, object]]:
        content = self.path.read_text(encoding="utf-8")
        return json.loads(content or "[]")

    def _write(self, data: List[Dict[str, object]]) -> None:
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def list_users(self) -> List[UserAccount]:
        return [UserAccount.from_dict(record) for record in self._read()]

    def get_by_id(self, user_id: str) -> Optional[UserAccount]:
        return next((u for u in self.list_users() if u.user_id == user_id), None)

    def get_by_email(self, email: str) -> Optional[UserAccount]:
        return next((u for u in self.list_users() if u.email.lower() == email.lower()), None)

    def save(self, account: UserAccount) -> None:
        users = self._read()
        existing = next((item for item in users if item["user_id"] == account.user_id), None)
        if existing:
            users = [account.to_dict() if item["user_id"] == account.user_id else item for item in users]
        else:
            users.append(account.to_dict())
        self._write(users)

    def add(self, account: UserAccount) -> None:
        if self.get_by_email(account.email):
            raise ValidationError("Email already registered")
        self.save(account)


class RegistrationService:
    def __init__(self, store: Optional[UserStore] = None):
        self.store = store or UserStore()

    def _ensure_admin(self, admin_id: str) -> UserAccount:
        admin = self.store.get_by_id(admin_id)
        if not admin:
            raise NotFoundError("Admin user not found")
        if admin.role != Role.ADMIN:
            raise AuthorizationError("Admin privileges required")
        return admin

    def register_user(self, data: Dict[str, object]) -> UserAccount:
        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip()
        password = str(data.get("password", ""))
        role = Role(data.get("role", Role.USER))

        if not name:
            raise ValidationError("Name is required")
        _validate_email(email)
        _validate_password(password)
        if role not in {Role.USER, Role.ORGANIZATION, Role.ADMIN}:
            raise ValidationError("Invalid role")

        organization_name = None
        verification_docs: List[str] = []
        verification_status = VerificationStatus.NOT_REQUIRED

        if role == Role.ORGANIZATION:
            organization_name = str(data.get("organization_name", "")).strip()
            verification_docs = list(data.get("verification_docs", []))
            if not organization_name:
                raise ValidationError("Organization name is required for organization users")
            if not verification_docs:
                raise ValidationError("Verification documents are required for organization registration")
            verification_status = VerificationStatus.PENDING

        if self.store.get_by_email(email):
            raise ValidationError("Email already registered")

        account = UserAccount(
            user_id=uuid.uuid4().hex,
            name=name,
            email=email,
            role=role,
            password_hash=_hash_password(password),
            organization_name=organization_name,
            verification_docs=verification_docs,
            verification_status=verification_status,
            account_status=AccountStatus.ACTIVE,
        )
        self.store.add(account)
        return account

    def approve_organization(self, admin_id: str, user_id: str) -> UserAccount:
        self._ensure_admin(admin_id)
        account = self.store.get_by_id(user_id)
        if not account:
            raise NotFoundError("User not found")
        if account.role != Role.ORGANIZATION:
            raise ValidationError("Only organization accounts require approval")
        account.verification_status = VerificationStatus.APPROVED
        account.updated_at = _now_iso()
        self.store.save(account)
        return account

    def reject_organization(self, admin_id: str, user_id: str) -> UserAccount:
        self._ensure_admin(admin_id)
        account = self.store.get_by_id(user_id)
        if not account:
            raise NotFoundError("User not found")
        if account.role != Role.ORGANIZATION:
            raise ValidationError("Only organization accounts require rejection")
        account.verification_status = VerificationStatus.REJECTED
        account.updated_at = _now_iso()
        self.store.save(account)
        return account

    def suspend_account(self, admin_id: str, user_id: str) -> UserAccount:
        self._ensure_admin(admin_id)
        return self._update_account_status(user_id, AccountStatus.SUSPENDED)

    def remove_account(self, admin_id: str, user_id: str) -> UserAccount:
        self._ensure_admin(admin_id)
        return self._update_account_status(user_id, AccountStatus.REMOVED)

    def _update_account_status(self, user_id: str, status: AccountStatus) -> UserAccount:
        account = self.store.get_by_id(user_id)
        if not account:
            raise NotFoundError("User not found")
        account.account_status = status
        account.updated_at = _now_iso()
        self.store.save(account)
        return account

    def update_account(self, user_id: str, data: Dict[str, object]) -> UserAccount:
        account = self.store.get_by_id(user_id)
        if not account:
            raise NotFoundError("User not found")
        if account.account_status != AccountStatus.ACTIVE:
            raise ValidationError("Cannot update inactive account")

        if name := str(data.get("name", "")).strip():
            account.name = name
        if email := str(data.get("email", "")).strip():
            _validate_email(email)
            existing = self.store.get_by_email(email)
            if existing and existing.user_id != user_id:
                raise ValidationError("Email already registered")
            account.email = email
        if password := str(data.get("password", "")):
            _validate_password(password)
            account.password_hash = _hash_password(password)

        account.updated_at = _now_iso()
        self.store.save(account)
        return account

    def authenticate(self, email: str, password: str) -> UserAccount:
        account = self.store.get_by_email(email)
        if not account:
            raise AuthorizationError("Invalid credentials")
        if account.password_hash != _hash_password(password):
            raise AuthorizationError("Invalid credentials")
        if account.account_status != AccountStatus.ACTIVE:
            raise AuthorizationError(f"Account is {account.account_status.value}")
        return account
