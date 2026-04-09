export function trackStatusHistory(taskId, statuses) {
  return {
    taskId,
    history: statuses,
  };
}

export function generateMonthlyReport(deliveries) {
  const completed = deliveries.filter(d => d.status === "delivered");
  return {
    totalDeliveries: completed.length,
    totalQuantity: completed.reduce((sum, d) => sum + (d.quantity || 0), 0),
    impactSummary: "Monthly redistribution report generated successfully.",
  };
}t