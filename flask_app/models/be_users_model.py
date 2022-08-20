from flask_app import app
from flask import flash
from flask_app.config.be_connection import MySQLConnection
from flask_app.models import be_cars_model
from flask_bcrypt import Bcrypt
import re

db = "be2"
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
FNAME_REGEX = re.compile(r'^[a-zA-Z.-]+$')
LNAME_REGEX = re.compile(r'^[a-zA-Z.-]+$')


class Users:
    def __init__(self, db_data):
        self.user_id = db_data['user_id']
        self.first_name = db_data['first_name']
        self.last_name = db_data['last_name']
        self.email = db_data['email']
        self.password = db_data['password']
        self.created_at = db_data['created_at']
        self.updated_at = db_data['updated_at']
        self.cars_owned = []

    @classmethod
    def save_users(cls, data):
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at)" \
                "VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, NOW(), NOW());"
        results = MySQLConnection(db).query_db(query, data)
        return results

    @classmethod
    def get_all_users(cls):
        query = "SELECT * FROM users;"
        results = MySQLConnection(db).query_db(query)
        users = []

        for user in results:
            users.append(cls(user))

        return users

    @classmethod
    def get_user_by_email(cls, data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = MySQLConnection(db).query_db(query, data)

        if len(results) < 1:
            return False
        return cls(results[0])

    @classmethod
    def purchase_cars(cls,data):
        query = "INSERT INTO car_owner (users_users_id, cars_car_id) VALUES (%(user_id)s, %(car_id)s)"
        results = MySQLConnection(db).query_db(query, data)
        return results

    @classmethod
    def get_user_by_id(cls, data):
        query = "SELECT * FROM users LEFT JOIN car_owner ON users.user_id = car_owner.users_users_id LEFT JOIN cars ON " \
                "car_id = car_owner.cars_car_id WHERE users.user_id = %(user_id)s;"
        results = MySQLConnection(db).query_db(query, data)


        users = cls(results[0])

        for row in results:
            if row['car_id'] == None:
                break

            data = {
                "car_id": row['car_id'],
                "model": row['model'],
                "make": row['make'],
                "year": row['year'],
                "price": row['price'],
                "seller_id": row['seller_id'],
                "was_sold": row['was_sold'],
                "description": row['description'],
                "created_at": row['cars.created_at'],
                "updated_at": row['cars.updated_at']
            }
            users.cars_owned.append(be_cars_model.Cars(data))
        return users

    @classmethod
    def add_car(cls, data):
        query = "INSERT INTO car_owner (users_users_id, cars_car_id) VALUES (%(user_id)s, %(car_id)s);"
        results = MySQLConnection(db).query_db(query, data)
        return results

    @staticmethod
    def validate_register(user):
        is_valid = True
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = MySQLConnection(db).query_db(query, user)
        if len(results) >= 1:
            flash("Email already taken.", "register")
            is_valid = False
        if not EMAIL_REGEX.match(user['email']):
            flash("Invalid Email.", "register")
            is_valid = False
        if not FNAME_REGEX.match(user['first_name']):
            flash("Name contains invalid characters")
            is_valid = False
        if len(user['first_name']) < 3:
            flash("First name must contain at least 3 characters", "register")
            is_valid = False
        if not LNAME_REGEX.match(user['last_name']):
            flash("Name contains invalid characters")
            is_valid = False
        if len(user['last_name']) < 3:
            flash("Last name must contain at least 3 characters", "register")
            is_valid = False
        if len(user['password']) < 8:
            flash("Password must contain at least 8 characters", "register")
            is_valid = False
        if user['password'] != user['confirm']:
            flash("Passwords don't match", "register")
        return is_valid
