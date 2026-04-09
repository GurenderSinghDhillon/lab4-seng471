from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class FoodNeed:
    organization_name: str
    contact_email: str
    location: str
    food_type: str
    quantity: str
    dietary_preferences: List[str] = field(default_factory=list)
    urgency_level: str = "normal"
    additional_notes: Optional[str] = None

    def is_valid(self) -> bool:
        required_fields = [
            self.organization_name,
            self.contact_email,
            self.location,
            self.food_type,
            self.quantity,
        ]
        return all(bool(field and field.strip()) for field in required_fields)


def create_food_need(data: dict) -> FoodNeed:
    return FoodNeed(
        organization_name=data.get("organization_name", ""),
        contact_email=data.get("contact_email", ""),
        location=data.get("location", ""),
        food_type=data.get("food_type", ""),
        quantity=data.get("quantity", ""),
        dietary_preferences=data.get("dietary_preferences", []),
        urgency_level=data.get("urgency_level", "normal"),
        additional_notes=data.get("additional_notes"),
    )


# Requirements draft
# 1. The system must allow a community organization to submit food needs and preferences.
# 2. Food need entries must include organization name, contact email, location, food type, and quantity.
# 3. The system must support dietary preferences such as vegan, gluten-free, nut-free, and halal.
# 4. Entries should allow optional urgency level and additional notes.
# 5. Validation must ensure all required fields are present and non-empty.

# Acceptance criteria
# - Given a valid food need submission, the system creates a FoodNeed instance successfully.
# - Given missing required fields, the submission is rejected or flagged as invalid.
# - Given dietary preferences, they are stored and retrievable in the FoodNeed structure.
# - Given optional urgency and notes, they are accepted without breaking the data structure.
