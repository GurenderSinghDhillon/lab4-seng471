from dataclasses import dataclass
from typing import List, Optional
import unittest

@dataclass
class Donation:
    id: int
    location: str
    food_type: str
    dietary_restrictions: List[str]
    quantity: int


def filter_donations(
    donations: List[Donation],
    location: Optional[str] = None,
    food_type: Optional[str] = None,
    dietary_restrictions: Optional[List[str]] = None,
    min_quantity: Optional[int] = None,
    max_quantity: Optional[int] = None,
) -> List[Donation]:
    """Return donations matching all supplied filter parameters."""
    filtered = []
    for donation in donations:
        if location and donation.location.lower() != location.lower():
            continue
        if food_type and donation.food_type.lower() != food_type.lower():
            continue
        if dietary_restrictions:
            if not all(
                restriction.lower() in (r.lower() for r in donation.dietary_restrictions)
                for restriction in dietary_restrictions
            ):
                continue
        if min_quantity is not None and donation.quantity < min_quantity:
            continue
        if max_quantity is not None and donation.quantity > max_quantity:
            continue
        filtered.append(donation)
    return filtered


class TestDonationFilter(unittest.TestCase):
    def setUp(self):
        self.donations = [
            Donation(id=1, location="Downtown", food_type="Vegetables", dietary_restrictions=["Vegan"], quantity=20),
            Donation(id=2, location="Uptown", food_type="Bakery", dietary_restrictions=["Nut-free"], quantity=15),
            Donation(id=3, location="Downtown", food_type="Canned Goods", dietary_restrictions=["Gluten-free"], quantity=30),
            Donation(id=4, location="Midtown", food_type="Fruits", dietary_restrictions=["Vegan", "Gluten-free"], quantity=10),
            Donation(id=5, location="Downtown", food_type="Bakery", dietary_restrictions=["Vegetarian"], quantity=5),
        ]

    def test_filter_by_location(self):
        result = filter_donations(self.donations, location="Downtown")
        self.assertEqual({d.id for d in result}, {1, 3, 5})

    def test_filter_by_food_type(self):
        result = filter_donations(self.donations, food_type="Bakery")
        self.assertEqual({d.id for d in result}, {2, 5})

    def test_filter_by_dietary_restrictions(self):
        result = filter_donations(self.donations, dietary_restrictions=["Vegan"])
        self.assertEqual({d.id for d in result}, {1, 4})

    def test_filter_by_multiple_restrictions(self):
        result = filter_donations(self.donations, dietary_restrictions=["Vegan", "Gluten-free"])
        self.assertEqual({d.id for d in result}, {4})

    def test_filter_by_quantity_range(self):
        result = filter_donations(self.donations, min_quantity=10, max_quantity=20)
        self.assertEqual({d.id for d in result}, {1, 2, 4})

    def test_filter_combined_criteria(self):
        result = filter_donations(
            self.donations,
            location="Downtown",
            food_type="Canned Goods",
            dietary_restrictions=["Gluten-free"],
            min_quantity=25,
        )
        self.assertEqual({d.id for d in result}, {3})


if __name__ == "__main__":
    unittest.main()
