from flask import Flask, render_template, request, redirect, url_for
import pymysql
import os

app = Flask(__name__)


def get_db_connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME"),
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )


def init_db():
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    phone VARCHAR(20),
                    city VARCHAR(100)
                )
            """)

        connection.commit()

    finally:
        connection.close()


@app.route("/")
def users():
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users ORDER BY id")
            user_list = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "users.html",
        users=user_list
    )


@app.route("/add", methods=["GET", "POST"])
def add_user():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        city = request.form["city"]

        connection = get_db_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users
                    (name, email, phone, city)
                    VALUES (%s, %s, %s, %s)
                """, (name, email, phone, city))

            connection.commit()

        finally:
            connection.close()

        return redirect(url_for("users"))

    return render_template(
        "user_form.html",
        title="Add User",
        user=None
    )


@app.route("/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )

            user = cursor.fetchone()

        if user is None:
            return "User not found", 404

        if request.method == "POST":

            name = request.form["name"]
            email = request.form["email"]
            phone = request.form["phone"]
            city = request.form["city"]

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE users
                    SET name = %s,
                        email = %s,
                        phone = %s,
                        city = %s
                    WHERE id = %s
                """, (
                    name,
                    email,
                    phone,
                    city,
                    user_id
                ))

            connection.commit()

            return redirect(url_for("users"))

    finally:
        connection.close()

    return render_template(
        "user_form.html",
        title="Edit User",
        user=user
    )


@app.route("/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM users WHERE id = %s",
                (user_id,)
            )

        connection.commit()

    finally:
        connection.close()

    return redirect(url_for("users"))


if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )

