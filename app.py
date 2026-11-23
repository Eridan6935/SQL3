from flask import Flask, request, redirect, url_for
import pymysql

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",        # свой пароль от MySQL
    "database": "flask_auth",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}


class Database:
    """Инкапсуляция работы с БД: подключение, запросы, закрытие соединения."""

    def __init__(self, config: dict):
        self.config = config

    def get_user(self, username: str):
        """Возвращает запись пользователя из users или None."""
        connection = pymysql.connect(**self.config)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id, user_name, user_password FROM users WHERE user_name = %s",
                    (username,),
                )
                return cursor.fetchone()
        finally:
            connection.close()


db = Database(DB_CONFIG)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            return "Заполните логин и пароль", 400

        user = db.get_user(username)
        if user is None:
            return "Пользователь не найден", 404
        if user["user_password"] != password:
            return "Неверный пароль", 401

        return redirect(url_for("profile", username=user["user_name"]))

    return """<!doctype html>
<html lang="ru">
<head><meta charset="utf-8"><title>Вход</title></head>
<body>
  <h1>Вход</h1>
  <form method="post">
    <input type="text" name="username" placeholder="Логин" required><br><br>
    <input type="password" name="password" placeholder="Пароль" required><br><br>
    <button type="submit">Войти</button>
  </form>
</body>
</html>"""


@app.route("/profile/<username>")
def profile(username):
    return f"Привет, {username}! Вы вошли в систему."


if __name__ == "__main__":
    app.run(debug=True)
