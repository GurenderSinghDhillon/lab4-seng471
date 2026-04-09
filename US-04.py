from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional
import unittest


@dataclass
class DonationListing:
    donor_name: str
    food_type: str
    quantity: int
    expiry_time: datetime
    allergens: List[str] = field(default_factory=list)
    dietary_information: List[str] = field(default_factory=list)
    description: Optional[str] = None
    pickup_location: Optional[str] = None

    def is_valid(self) -> bool:
        required_text_fields = [self.donor_name, self.food_type]
        if not all(bool(field and field.strip()) for field in required_text_fields):
            return False
        if not isinstance(self.quantity, int) or self.quantity <= 0:
            return False
        if not isinstance(self.expiry_time, datetime):
            return False
        if self.expiry_time <= datetime.now():
            return False
        return True


def create_donation_listing(data: dict) -> DonationListing:
    return DonationListing(
        donor_name=data.get("donor_name", ""),
        food_type=data.get("food_type", ""),
        quantity=data.get("quantity", 0),
        expiry_time=data.get("expiry_time"),
        allergens=data.get("allergens", []),
        dietary_information=data.get("dietary_information", []),
        description=data.get("description"),
        pickup_location=data.get("pickup_location"),
    )


# Requirements draft
# 1. The system must allow a donor to create a donation listing for available food.
# 2. A donation listing must include donor name, food type, quantity, and expiry time.
# 3. The system must support additional food details such as allergens and dietary information.
# 4. The system should allow optional description and pickup location fields.
# 5. Validation must ensure required fields are present, quantity is greater than zero,
#    and expiry time is in the future.

# Validation rules
# - donor_name is required and cannot be blank.
# - food_type is required and cannot be blank.
# - quantity is required and must be a positive integer.
# - expiry_time is required and must be a valid datetime later than the current time.
# - allergens and dietary_information are optional but should be stored if provided.

# Acceptance criteria
# - Given a donor enters all required fields correctly, the system creates a donation listing.
# - Given a required field is missing or blank, the listing is marked invalid.
# - Given quantity is zero or negative, the listing is marked invalid.
# - Given expiry time is in the past, the listing is marked invalid.
# - Given allergens and dietary information are supplied, the system stores them with the listing.


class TestDonationListing(unittest.TestCase):
    def test_create_valid_donation_listing(self):
        listing = create_donation_listing(
            {
                "donor_name": "Campus Cafe",
                "food_type": "Sandwiches",
                "quantity": 15,
                "expiry_time": datetime.now() + timedelta(hours=3),
                "allergens": ["Gluten", "Dairy"],
                "dietary_information": ["Vegetarian"],
                "description": "Prepared this morning",
                "pickup_location": "Student Center",
            }
        )
        self.assertTrue(listing.is_valid())
        self.assertEqual(listing.food_type, "Sandwiches")
        self.assertIn("Gluten", listing.allergens)
        self.assertIn("Vegetarian", listing.dietary_information)

    def test_missing_food_type_is_invalid(self):
        listing = create_donation_listing(
            {
                "donor_name": "Campus Cafe",
                "food_type": "",
                "quantity": 10,
                "expiry_time": datetime.now() + timedelta(hours=2),
            }
        )
        self.assertFalse(listing.is_valid())

    def test_quantity_must_be_positive(self):
        listing = create_donation_listing(
            {
                "donor_name": "Campus Cafe",
                "food_type": "Fruit",
                "quantity": 0,
                "expiry_time": datetime.now() + timedelta(hours=2),
            }
        )
        self.assertFalse(listing.is_valid())

    def test_expiry_time_must_be_in_future(self):
        listing = create_donation_listing(
            {
                "donor_name": "Campus Cafe",
                "food_type": "Salad",
                "quantity": 5,
                "expiry_time": datetime.now() - timedelta(minutes=10),
            }
        )
        self.assertFalse(listing.is_valid())

    def test_optional_fields_are_preserved(self):
        listing = create_donation_listing(
            {
                "donor_name": "Bakery Hub",
                "food_type": "Bread",
                "quantity": 8,
                "expiry_time": datetime.now() + timedelta(days=1),
                "allergens": ["Wheat"],
                "dietary_information": ["Halal"],
            }
        )
        self.assertTrue(listing.is_valid())
        self.assertEqual(listing.allergens, ["Wheat"])
        self.assertEqual(listing.dietary_information, ["Halal"])


if __name__ == "__main__":
    unittest.main()
