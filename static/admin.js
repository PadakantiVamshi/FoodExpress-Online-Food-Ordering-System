
async function loadDashboard() {

    try {
        const response = await fetch("/api/admin/dashboard");

        if (!response.ok) {
            throw new Error("Unable to load dashboard");
        }

        const data = await response.json();
        const stats = data.stats;

        document.getElementById("total-orders").textContent =
            stats.total_orders;

        document.getElementById("total-revenue").textContent =
            "$" + Number(stats.total_revenue).toFixed(2);

        document.getElementById("total-customers").textContent =
            stats.total_customers;

        document.getElementById("pending-orders").textContent =
            stats.pending_orders;

        const table = document.getElementById("orders-table");

        table.innerHTML = "";

        data.orders.forEach(order => {

            const row = table.insertRow();

          const values = [
    order.order_id,
    order.customer_name,
    new Date(order.order_date).toLocaleDateString(),
    "$" + Number(order.total_amount).toFixed(2),
    order.order_status
];

values.forEach(value => {
    const cell = row.insertCell();
    cell.textContent = value;
});

const actionCell = row.insertCell();

const dropdown = document.createElement("select");

const statuses = [
    "Pending",
    "Preparing",
    "Out for Delivery",
    "Delivered",
    "Cancelled"
];

statuses.forEach(status => {
    const option = document.createElement("option");
    option.value = status;
    option.textContent = status;
    dropdown.appendChild(option);
});

dropdown.value = order.order_status;
dropdown.addEventListener("change", async () => {
    try {
        const response = await fetch(
            `/api/orders/${order.order_id}/status`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    order_status: dropdown.value
                })
            }
        );

        const result = await response.json();

        if (response.ok) {
            alert("Order status updated successfully!");
            location.reload();
        } else {
            alert(result.error || "Update failed!");
            dropdown.value = order.order_status;
        }

    } catch (error) {
        alert("Unable to update order status.");
        dropdown.value = order.order_status;
    }
});

actionCell.appendChild(dropdown);  

        });

    } catch (error) {
        console.error(error);
        alert("Failed to load dashboard data.");
    }
}

loadDashboard();
