export function getAvailableDeliveryTasks() {
  return [
    {
      id: "TASK-1",
      pickupLocation: "Calgary Grocery Store",
      destination: "Downtown Food Bank",
      quantity: "10 boxes",
      pickupDeadline: "2026-04-08 17:00",
      status: "available",
    },
    {
      id: "TASK-2",
      pickupLocation: "Restaurant A",
      destination: "Community Shelter",
      quantity: "6 trays",
      pickupDeadline: "2026-04-08 18:30",
      status: "available",
    },
  ];
}