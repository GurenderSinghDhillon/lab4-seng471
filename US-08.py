from dataclasses import dataclass
from enum import Enum, auto
import unittest


class DonationStatus(Enum):
    AVAILABLE = auto()
    CLAIMED = auto()
    RESERVED = auto()
    PICKED_UP = auto()
    CANCELLED = auto()


@dataclass
class Donation:
    donation_id: str
    description: str
    pickup_available: bool
    delivery_available: bool
    status: DonationStatus = DonationStatus.AVAILABLE
    claimed_by: str | None = None
    confirmation_message: str | None = None

    def is_claimable(self) -> bool:
        return self.status == DonationStatus.AVAILABLE

    def claim(self, recipient_id: str, method: str) -> bool:
        if not self.is_claimable():
            return False
        if method not in ("pickup", "delivery"):
            return False
        if method == "pickup" and not self.pickup_available:
            return False
        if method == "delivery" and not self.delivery_available:
            return False

        self.claimed_by = recipient_id
        self.status = DonationStatus.CLAIMED
        self.confirmation_message = (
            f"Donation {self.donation_id} reserved for {method} by recipient {recipient_id}."
        )
        return True

    def confirm(self) -> bool:
        if self.status != DonationStatus.CLAIMED:
            return False
        self.status = DonationStatus.RESERVED
        self.confirmation_message = f"Donation {self.donation_id} confirmed for recipient {self.claimed_by}."
        return True


@dataclass
class Recipient:
    recipient_id: str
    name: str
    verified: bool = True

    def claim_donation(self, donation: Donation, method: str) -> bool:
        if not self.verified:
            return False
        return donation.claim(self.recipient_id, method)


class ClaimWorkflow:
    """Claiming workflow for donations.

    Requirements:
    - Donation must be available.
    - Recipient must be verified.
    - Pickup or delivery option must be supported by the donation.
    - Claims are not allowed once a donation is already claimed or reserved.

    Acceptance / Confirmation:
    - Successful claim transitions donation to CLAIMED.
    - Recipient receives a confirmation message.
    - Confirmation step transitions donation to RESERVED.
    - Status and claimed_by fields are asserted in acceptance tests.
    """

    @staticmethod
    def can_claim(donation: Donation, recipient: Recipient, method: str) -> bool:
        return donation.is_claimable() and recipient.verified and method in ("pickup", "delivery")


class TestClaimWorkflow(unittest.TestCase):
    def test_claim_available_donation_for_pickup(self):
        donation = Donation("D001", "Canned food", pickup_available=True, delivery_available=False)
        recipient = Recipient("R001", "Alice")

        self.assertTrue(recipient.claim_donation(donation, "pickup"))
        self.assertEqual(donation.status, DonationStatus.CLAIMED)
        self.assertEqual(donation.claimed_by, recipient.recipient_id)
        self.assertIn("reserved for pickup", donation.confirmation_message)

    def test_confirm_claimed_donation(self):
        donation = Donation("D002", "Blankets", pickup_available=True, delivery_available=True)
        recipient = Recipient("R002", "Bob")

        recipient.claim_donation(donation, "delivery")
        self.assertTrue(donation.confirm())
        self.assertEqual(donation.status, DonationStatus.RESERVED)
        self.assertIn("confirmed for recipient", donation.confirmation_message)

    def test_cannot_claim_unavailable_donation(self):
        donation = Donation("D003", "Books", pickup_available=False, delivery_available=False)
        recipient = Recipient("R003", "Carol")

        self.assertFalse(recipient.claim_donation(donation, "pickup"))
        self.assertEqual(donation.status, DonationStatus.AVAILABLE)
        self.assertIsNone(donation.claimed_by)

    def test_unverified_recipient_cannot_claim(self):
        donation = Donation("D004", "Clothes", pickup_available=True, delivery_available=True)
        recipient = Recipient("R004", "Dan", verified=False)

        self.assertFalse(recipient.claim_donation(donation, "delivery"))
        self.assertEqual(donation.status, DonationStatus.AVAILABLE)

    def test_claim_fails_when_already_claimed(self):
        donation = Donation("D005", "Furniture", pickup_available=True, delivery_available=True)
        recipient1 = Recipient("R005", "Eve")
        recipient2 = Recipient("R006", "Frank")

        self.assertTrue(recipient1.claim_donation(donation, "pickup"))
        self.assertFalse(recipient2.claim_donation(donation, "delivery"))
        self.assertEqual(donation.claimed_by, recipient1.recipient_id)


if __name__ == "__main__":
    unittest.main()
