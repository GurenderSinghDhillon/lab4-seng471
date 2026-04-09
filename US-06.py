from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List
import unittest


@dataclass
class DonationListing:
    listing_id: str
    food_type: str
    quantity: int
    expiry_time: datetime
    pickup_location: str
    dietary_information: List[str] = field(default_factory=list)
    allergens: List[str] = field(default_factory=list)
    available: bool = True

    def is_visible(self) -> bool:
        return self.available and self.expiry_time > datetime.now()


def browse_available_donations(listings: List[DonationListing]) -> List[DonationListing]:
    return [listing for listing in listings if listing.is_visible()]


def get_display_data(listing: DonationListing) -> dict:
    return {
        "listing_id": listing.listing_id,
        "food_type": listing.food_type,
        "quantity": listing.quantity,
        "expiry_time": listing.expiry_time,
        "pickup_location": listing.pickup_location,
        "dietary_information": listing.dietary_information,
        "allergens": listing.allergens,
    }


# Browsing workflow
# 1. A user opens the donation listings page.
# 2. The system retrieves donation listings that are currently available.
# 3. The system hides expired or unavailable listings.
# 4. The user browses the remaining listings and views key donation details.
# 5. The user can identify listings that match their food and dietary needs.

# Displayed donation data
# - Listing ID
# - Food type
# - Quantity
# - Expiry time
# - Pickup location
# - Dietary information
# - Allergen information

# Acceptance criteria
# - Given active donation listings exist, the system displays them to the user.
# - Given a listing is expired, the system does not display it.
# - Given a listing is unavailable, the system does not display it.
# - Given a user views a listing, the system shows the required donation details.
# - Given multiple listings are available, the system returns all visible listings.


class TestBrowseDonations(unittest.TestCase):
    def setUp(self):
        self.listings = [
            DonationListing(
                listing_id="D001",
                food_type="Apples",
                quantity=20,
                expiry_time=datetime.now() + timedelta(hours=5),
                pickup_location="North Campus",
                dietary_information=["Vegan"],
                allergens=[],
                available=True,
            ),
            DonationListing(
                listing_id="D002",
                food_type="Bread",
                quantity=10,
                expiry_time=datetime.now() - timedelta(minutes=30),
                pickup_location="South Campus",
                dietary_information=["Vegetarian"],
                allergens=["Wheat"],
                available=True,
            ),
            DonationListing(
                listing_id="D003",
                food_type="Soup",
                quantity=8,
                expiry_time=datetime.now() + timedelta(hours=2),
                pickup_location="Downtown Kitchen",
                dietary_information=["Halal"],
                allergens=["Celery"],
                available=False,
            ),
        ]

    def test_browse_returns_only_visible_listings(self):
        result = browse_available_donations(self.listings)
        self.assertEqual([listing.listing_id for listing in result], ["D001"])

    def test_expired_listing_is_hidden(self):
        result = browse_available_donations([self.listings[1]])
        self.assertEqual(result, [])

    def test_unavailable_listing_is_hidden(self):
        result = browse_available_donations([self.listings[2]])
        self.assertEqual(result, [])

    def test_display_data_contains_required_fields(self):
        display_data = get_display_data(self.listings[0])
        self.assertEqual(display_data["food_type"], "Apples")
        self.assertEqual(display_data["quantity"], 20)
        self.assertEqual(display_data["pickup_location"], "North Campus")
        self.assertEqual(display_data["dietary_information"], ["Vegan"])

    def test_multiple_visible_listings_are_returned(self):
        extra_listing = DonationListing(
            listing_id="D004",
            food_type="Rice",
            quantity=15,
            expiry_time=datetime.now() + timedelta(days=1),
            pickup_location="West End",
            dietary_information=["Gluten-free"],
            allergens=[],
            available=True,
        )

        result = browse_available_donations([self.listings[0], extra_listing])
        self.assertEqual({listing.listing_id for listing in result}, {"D001", "D004"})


if __name__ == "__main__":
    unittest.main()
