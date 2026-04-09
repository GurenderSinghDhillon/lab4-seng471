export function acceptTask(task) {
  if (task.status !== "available") {
    throw new Error("Task cannot be accepted");
  }
  return { ...task, status: "accepted" };
}

export function markPickedUp(task) {
  if (task.status !== "accepted") {
    throw new Error("Task must be accepted before pickup");
  }
  return { ...task, status: "picked_up" };
}

export function markDelivered(task) {
  if (task.status !== "picked_up") {
    throw new Error("Task must be picked up before delivery");
  }
  return { ...task, status: "delivered" };
}