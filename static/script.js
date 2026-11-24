
let menu = [];
let cart = [];

const foodIcons = {
    Pizza: "🍕",
    Burgers: "🍔",
    Biryani: "🍛",
    Desserts: "🍰",
    Beverages: "🥤"
};

async function loadMenu() {
    try {
        const response = await fetch("/api/menu");

        if (!response.ok) {
            throw new Error("Unable to load menu");
        }

        menu = await response.json();

        const categories = [
            ...new Set(menu.map(item => item.category_name))
        ];

        const select = document.getElementById("category");

        categories.forEach(category => {
            const option = document.createElement("option");
            option.value = category;
            option.textContent = category;
            select.appendChild(option);
        });

        displayMenu(menu);

    } catch (error) {
        document.getElementById("menu-container").textContent =
            "Unable to load food items.";
        console.error(error);
    }
}

function displayMenu(items) {
    const container = document.getElementById("menu-container");
    container.replaceChildren();

    items.forEach(item => {
        const card = document.createElement("div");
        card.className = "food-card";

        const icon = document.createElement("div");
        icon.className = "food-icon";
        icon.textContent = foodIcons[item.category_name] || "🍽️";

        const details = document.createElement("div");
        details.className = "food-details";

        const name = document.createElement("h3");
        name.textContent = item.item_name;

        const description = document.createElement("p");
        description.textContent = item.description || "";

        const category = document.createElement("p");
        category.textContent = item.category_name;

        const price = document.createElement("div");
        price.className = "price";
        price.textContent = "$" + Number(item.price).toFixed(2);

        const button = document.createElement("button");
        button.textContent = item.availability
            ? "Add to Cart" : "Unavailable";

        button.disabled = !item.availability;
        button.onclick = () => addToCart(item.item_id);

        details.append(name, description, category, price, button);
        card.append(icon, details);
        container.appendChild(card);
    });

    if (items.length === 0) {
        container.textContent = "No food items found.";
    }
}

function filterMenu() {
    const search = document.getElementById("search")
        .value.toLowerCase();

    const category = document.getElementById("category").value;

    const filtered = menu.filter(item =>
        item.item_name.toLowerCase().includes(search) &&
        (category === "All" || item.category_name === category)
    );

    displayMenu(filtered);
}

function addToCart(id) {
    const item = menu.find(food => food.item_id === id);

    if (!item || !item.availability) return;

    const existing = cart.find(food => food.item_id === id);

    if (existing) {
        existing.quantity++;
    } else {
        cart.push({ ...item, quantity: 1 });
    }

    displayCart();
}

function removeFromCart(id) {
    cart = cart.filter(item => item.item_id !== id);
    displayCart();
}

function displayCart() {
    const container = document.getElementById("cart-items");
    container.replaceChildren();

    let total = 0;

    cart.forEach(item => {
        const subtotal = Number(item.price) * item.quantity;
        total += subtotal;

        const row = document.createElement("div");
        row.className = "cart-row";

        const label = document.createElement("span");
        label.textContent =
            `${item.item_name} x ${item.quantity} - $${subtotal.toFixed(2)}`;

        const button = document.createElement("button");
        button.textContent = "Remove";
        button.onclick = () => removeFromCart(item.item_id);

        row.append(label, button);
        container.appendChild(row);
    });

    if (cart.length === 0) {
        container.textContent = "Your cart is empty.";
    }

    document.getElementById("total").textContent =
        total.toFixed(2);
}

document.getElementById("search")
    .addEventListener("input", filterMenu);

document.getElementById("category")
    .addEventListener("change", filterMenu);


document.getElementById("checkout-btn")
    .addEventListener("click", async () => {

        const customerId = Number(
            document.getElementById("customer").value
        );

        const message = document.getElementById("order-message");
        const button = document.getElementById("checkout-btn");

        if (cart.length === 0) {
            alert("Your cart is empty!");
            return;
        }

        if (!customerId) {
            alert("Please select a customer!");
            return;
        }

        const order = {
            customer_id: customerId,
            items: cart.map(item => ({
                item_id: item.item_id,
                quantity: item.quantity
            }))
        };

        button.disabled = true;
        message.textContent = "Placing your order...";

        try {
            const response = await fetch("/api/orders", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(order)
            });

            const result = await response.json();

            if (response.ok) {
                message.style.color = "green";

                message.textContent =
                    "Order placed successfully! Order ID: " +
                    result.order_id +
                    " | Total: $" +
                    Number(result.total_amount).toFixed(2) +
                    " | Status: " +
                    result.order_status;

                cart = [];
                displayCart();

            } else {
                message.style.color = "red";
                message.textContent =
                    result.error || "Order failed!";
            }

        } catch (error) {
            message.style.color = "red";
            message.textContent =
                "Unable to connect to the server.";
        } finally {
            button.disabled = false;
        }
    });


loadMenu();
