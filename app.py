from flask import Flask, render_template, request, redirect, url_for, session
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "secret123"

# Login credentials
USERNAME = "admin"
PASSWORD = "1234"


# ---------------- LOGIN PAGE ----------------
@app.route("/")
def login():
    return render_template("login.html")


# ---------------- CHECK LOGIN ----------------
@app.route("/login", methods=["POST"])
def check_login():

    username = request.form.get("username")
    password = request.form.get("password")

    if username == USERNAME and password == PASSWORD:
        session["user"] = username
        return redirect(url_for("home"))
    else:
        return "Invalid Login"


# ---------------- SALES INPUT PAGE ----------------
@app.route("/home")
def home():

    if "user" in session:
        return render_template("index.html")

    return redirect(url_for("login"))


# ---------------- ANALYZE SALES ----------------
@app.route("/analyze", methods=["POST"])
def analyze():

    products = request.form.getlist("product")
    quantities = request.form.getlist("quantity")
    prices = request.form.getlist("price")

    product_data = {}
    total_revenue = 0
    max_qty = 0
    best_products = []

    # ---- CLEAN + MERGE DATA ----
    for i in range(len(products)):

        name = products[i].strip()

        if name == "":
            continue

        try:
            qty = int(quantities[i])
            price = float(prices[i])
        except:
            continue

        revenue = qty * price
        total_revenue += revenue

        # merge duplicate product names
        if name in product_data:
            product_data[name]["qty"] += qty
            product_data[name]["revenue"] += revenue
        else:
            product_data[name] = {"qty": qty, "revenue": revenue}

    # ---- FIND BEST SELLERS ----
    for product, data in product_data.items():

        if data["qty"] > max_qty:
            max_qty = data["qty"]
            best_products = [product]

        elif data["qty"] == max_qty:
            best_products.append(product)

    # ---- PREPARE CHART DATA ----
    labels = list(product_data.keys())
    revenues = [data["revenue"] for data in product_data.values()]

    if len(labels) == 0:
        return "No valid sales data entered."

    # Create static folder if missing
    os.makedirs("static", exist_ok=True)

    # ---- PIE CHART BASED ON REVENUE ----
    plt.figure()

    plt.pie(
        revenues,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90
    )

    plt.title("Revenue Distribution by Product")

    plt.savefig("static/sales_chart.png")
    plt.close()

    best_selling = ", ".join(best_products)

    return render_template(
        "result.html",
        revenue=round(total_revenue, 2),
        best=best_selling
    )


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():

    session.pop("user", None)
    return redirect(url_for("login"))


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)