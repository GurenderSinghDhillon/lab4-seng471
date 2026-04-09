from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import List, Optional
import unittest


class ListingStatus(Enum):
    ACTIVE = auto()
    CLAIMED = auto()
    CANCELLED = auto()


@dataclass
class DonationListing:
    listing_id: str
    donor_id: str
    food_type: str
    quantity: int
    expiry_time: datetime
    allergens: List[str] = field(default_factory=list)
    dietary_information: List[str] = field(default_factory=list)
    status: ListingStatus = ListingStatus.ACTIVE
    cancellation_reason: Optional[str] = None

    def is_editable(self) -> bool:
        return self.status == ListingStatus.ACTIVE

    def update_listing(
        self,
        food_type: Optional[str] = None,
        quantity: Optional[int] = None,
        expiry_time: Optional[datetime] = None,
        allergens: Optional[List[str]] = None,
        dietary_information: Optional[List[str]] = None,
    ) -> bool:
        if not self.is_editable():
            return False

        new_food_type = self.food_type if food_type is None else food_type
        new_quantity = self.quantity if quantity is None else quantity
        new_expiry_time = self.expiry_time if expiry_time is None else expiry_time

        if not new_food_type or not new_food_type.strip():
            return False
        if not isinstance(new_quantity, int) or new_quantity <= 0:
            return False
        if not isinstance(new_expiry_time, datetime) or new_expiry_time <= datetime.now():
            return False

        self.food_type = new_food_type
        self.quantity = new_quantity
        self.expiry_time = new_expiry_time
        if allergens is not None:
            self.allergens = allergens
        if dietary_information is not None:
            self.dietary_information = dietary_information
        return True

    def cancel_listing(self, reason: Optional[str] = None) -> bool:
        if self.status != ListingStatus.ACTIVE:
            return False
        self.status = ListingStatus.CANCELLED
        self.cancellation_reason = reason
        return True


class DonationListingManager:
    """Editing and cancellation workflow for donor listings.

    Requirements:
    - A donor can edit a listing while it is active.
    - Editable fields include food type, quantity, expiry time, allergens,
      and dietary information.
    - Updated values must still pass validation rules.
    - A donor can cancel a listing if the donation is no longer available.
    - Claimed or already cancelled listings cannot be edited or cancelled again.
    """

    @staticmethod
    def can_edit(listing: DonationListing) -> bool:
        return listing.status == ListingStatus.ACTIVE

    @staticmethod
    def can_cancel(listing: DonationListing) -> bool:
        return listing.status == ListingStatus.ACTIVE


# Requirements draft
# 1. The system must allow a donor to edit an existing active donation listing.
# 2. The system must allow a donor to cancel an active donation listing.
# 3. The system must prevent edits to claimed or cancelled listings.
# 4. The system must prevent cancelling a listing more than once.
# 5. Edited values must still satisfy listing validation rules.

# Edit/update workflow
# - A donor selects one of their active listings.
# - The donor updates one or more editable fields.
# - The system validates the updated information before saving changes.
# - If validation passes, the listing is updated and remains active.
# - If validation fails, the update is rejected and the original data remains unchanged.

# Cancellation rules
# - Only active listings can be cancelled.
# - Cancelled listings are no longer available to recipients.
# - Claimed listings cannot be cancelled by this workflow.
# - A cancellation reason may be stored, but it is optional.


class TestDonationListingManager(unittest.TestCase):
    def setUp(self):
        self.listing = DonationListing(
            listing_id="D100",
            donor_id="U100",
            food_type="Soup",
            quantity=12,
            expiry_time=datetime.now() + timedelta(hours=4),
            allergens=["Celery"],
            dietary_information=["Vegetarian"],
        )

    def test_active_listing_can_be_updated(self):
        result = self.listing.update_listing(
            food_type="Tomato Soup",
            quantity=10,
            dietary_information=["Vegetarian", "Gluten-free"],
        )

        self.assertTrue(result)
        self.assertEqual(self.listing.food_type, "Tomato Soup")
        self.assertEqual(self.listing.quantity, 10)
        self.assertIn("Gluten-free", self.listing.dietary_information)

    def test_update_fails_for_invalid_quantity(self):
        original_quantity = self.listing.quantity

        result = self.listing.update_listing(quantity=0)

        self.assertFalse(result)
        self.assertEqual(self.listing.quantity, original_quantity)

    def test_update_fails_for_cancelled_listing(self):
        self.listing.cancel_listing("Donation already picked up elsewhere")

        result = self.listing.update_listing(food_type="Bread")

        self.assertFalse(result)
        self.assertEqual(self.listing.food_type, "Soup")

    def test_active_listing_can_be_cancelled(self):
        result = self.listing.cancel_listing("Donation no longer available")

        self.assertTrue(result)
        self.assertEqual(self.listing.status, ListingStatus.CANCELLED)
        self.assertEqual(self.listing.cancellation_reason, "Donation no longer available")

    def test_claimed_listing_cannot_be_cancelled(self):
        self.listing.status = ListingStatus.CLAIMED

        result = self.listing.cancel_listing("Should not work")

        self.assertFalse(result)
        self.assertEqual(self.listing.status, ListingStatus.CLAIMED)


if __name__ == "__main__":
    unittest.main()
