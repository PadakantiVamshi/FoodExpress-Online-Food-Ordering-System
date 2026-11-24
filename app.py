from flask import Flask
from flask import jsonify
from db import get_db_connection
from flask import Flask, jsonify, request
from flask import Flask, jsonify, request, render_template

# Create Flask application
app = Flask(__name__)

# Home page route
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/menu", methods=["GET"])
def get_menu():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                m.item_id,
                m.item_name,
                m.description,
                m.price,
                m.availability,
                c.category_name
            FROM menu_items AS m
            INNER JOIN categories AS c
                ON m.category_id = c.category_id
        """)

        menu_items = cursor.fetchall()

        for item in menu_items:
            item["price"] = float(item["price"])

        return jsonify(menu_items)

    finally:
        cursor.close()
        conn.close()


@app.route("/api/menu", methods=["POST"])
def add_menu_item():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400

    required = ["category_id", "item_name", "price"]

    if any(data.get(field) is None for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        category_id = int(data["category_id"])
        price = float(data["price"])

        if price < 0 or not data["item_name"].strip():
            return jsonify({"error": "Invalid item name or price"}), 400

    except (ValueError, TypeError, AttributeError):
        return jsonify({"error": "Invalid input values"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO menu_items
            (category_id, item_name, description, price)
            VALUES (%s, %s, %s, %s)
            """,
            (
                category_id,
                data["item_name"],
                data.get("description", ""),
                price
            )
        )

        conn.commit()

        return jsonify({
            "message": "Food item added successfully",
            "item_id": cursor.lastrowid
        }), 201

    except Exception:
        conn.rollback()
        return jsonify({"error": "Unable to add food item"}), 400

    finally:
        cursor.close()
        conn.close()


@app.route("/api/menu/<int:item_id>", methods=["PUT"])
def update_menu_item(item_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON required"}), 400

    try:
        price = float(data["price"])
        if price < 0:
            raise ValueError()
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "Invalid price"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT item_id FROM menu_items WHERE item_id = %s",
            (item_id,)
        )

        if cursor.fetchone() is None:
            return jsonify({"error": "Item not found"}), 404

        cursor.execute("""
            UPDATE menu_items
            SET price = %s
            WHERE item_id = %s
        """, (price, item_id))

        conn.commit()

        return jsonify({
            "message": "Food item updated successfully"
        }), 200

    finally:
        cursor.close()
        conn.close()


@app.route("/api/menu/<int:item_id>", methods=["DELETE"])
def delete_menu_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM menu_items WHERE item_id = %s",
            (item_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Item not found"}), 404

        conn.commit()

        return jsonify({
            "message": "Food item deleted successfully"
        }), 200

    except Exception:
        conn.rollback()
        return jsonify({
            "error": "Unable to delete food item"
        }), 400

    finally:
        cursor.close()
        conn.close()



@app.route("/api/orders", methods=["POST"])
def place_order():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid order"}), 400

    customer_id = data.get("customer_id")
    items = data.get("items")

    if type(customer_id) is not int or not isinstance(items, list) or not items:
        return jsonify({"error": "Customer and items required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        conn.start_transaction()

        cursor.execute(
            "SELECT customer_id FROM customers WHERE customer_id = %s",
            (customer_id,)
        )

        if not cursor.fetchone():
            return jsonify({"error": "Customer not found"}), 404

        total_amount = 0
        order_details = []

        for item in items:
            item_id = item["item_id"]
            quantity = item["quantity"]

            if type(quantity) is not int or quantity <= 0:
                return jsonify({"error": "Invalid quantity"}), 400

            cursor.execute("""
                SELECT price, availability
                FROM menu_items
                WHERE item_id = %s
            """, (item_id,))

            food = cursor.fetchone()

            if not food or not food["availability"]:
                return jsonify({
                    "error": "Food item unavailable"
                }), 400

            unit_price = food["price"]
            total_amount += unit_price * quantity

            order_details.append(
                (item_id, quantity, unit_price)
            )

        cursor.execute("""
            INSERT INTO orders
            (customer_id, order_date, total_amount, order_status)
            VALUES (%s, NOW(), %s, 'Pending')
        """, (customer_id, total_amount))

        order_id = cursor.lastrowid

        for item_id, quantity, unit_price in order_details:

            cursor.execute("""
                INSERT INTO order_items
                (order_id, item_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
            """, (
                order_id,
                item_id,
                quantity,
                unit_price
            ))

        conn.commit()

        return jsonify({
            "message": "Order placed successfully!",
            "order_id": order_id,
            "total_amount": float(total_amount),
            "order_status": "Pending"
        }), 201

    except Exception as e:
        conn.rollback()
        print(e)
        return jsonify({"error": "Order failed"}), 400

    finally:
        conn.rollback()
        cursor.close()
        conn.close()

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/api/admin/dashboard", methods=["GET"])
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT COUNT(*) AS total_orders,
                   COALESCE(SUM(total_amount), 0) AS total_revenue
            FROM orders
        """)
        stats = cursor.fetchone()

        cursor.execute("""
            SELECT COUNT(*) AS total_customers
            FROM customers
        """)
        stats.update(cursor.fetchone())

        cursor.execute("""
            SELECT COUNT(*) AS pending_orders
            FROM orders
            WHERE order_status = 'Pending'
        """)
        stats.update(cursor.fetchone())

        cursor.execute("""
            SELECT o.order_id,
                   c.name AS customer_name,
                   o.order_date,
                   o.total_amount,
                   o.order_status
            FROM orders o
            JOIN customers c
            ON o.customer_id = c.customer_id
            ORDER BY o.order_id DESC
        """)
        orders = cursor.fetchall()

        stats["total_revenue"] = float(stats["total_revenue"])

        for order in orders:
            order["total_amount"] = float(order["total_amount"])

        return jsonify({
            "stats": stats,
            "orders": orders
        })

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
@app.route("/api/orders/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    data = request.get_json() or {}
    status = data.get("order_status")

    valid_statuses = [
        "Pending",
        "Preparing",
        "Out for Delivery",
        "Delivered",
        "Cancelled"
    ]

    if status not in valid_statuses:
        return jsonify({"error": "Invalid status"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT order_id FROM orders WHERE order_id = %s",
            (order_id,)
        )

        if cursor.fetchone() is None:
            return jsonify({"error": "Order not found"}), 404

        cursor.execute("""
            UPDATE orders
            SET order_status = %s
            WHERE order_id = %s
        """, (status, order_id))

        conn.commit()

        return jsonify({
            "message": "Order status updated successfully"
        }), 200

    except Exception as e:
        conn.rollback()
        print(e)
        return jsonify({"error": "Update failed"}), 500

    finally:
        cursor.close()
        conn.close()
        
# Run Flask application
if __name__ == "__main__":
    app.run(debug=True)