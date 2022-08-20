from flask_app import app
from flask import flash
from flask_app.config.be_connection import MySQLConnection
from flask_app.models import be_users_model

db = "be2"


class Cars:
    def __init__(self, db_data):
        self.car_id = db_data['car_id']
        self.model = db_data['model']
        self.make = db_data['make']
        self.price = db_data['price']
        self.year = db_data['year']
        self.description = db_data['description']
        self.seller_id = db_data['seller_id']
        self.was_sold = db_data['was_sold']
        self.created_at = db_data['created_at']
        self.updated_at = db_data['updated_at']

        self.owners = []

    @classmethod
    def get_all_cars(cls):
        query = "SELECT * FROM cars;"
        cars = []
        results = MySQLConnection(db).query_db(query)
        for row in results:
            cars.append(cls(row))

        return cars

    @classmethod
    def save_car(cls, data):
        query = "INSERT INTO cars (model, make, price, year, description, seller_id) VALUES (%(model)s, %(make)s, " \
                "%(price)s, %(year)s, %(description)s, %(seller_id)s);"
        results = MySQLConnection(db).query_db(query, data)
        return results

    @classmethod
    def get_car_by_id(cls, data):
        query = "SELECT * FROM cars WHERE car_id = %(car_id)s;"
        results = MySQLConnection(db).query_db(query, data)

        return cls(results[0])

    @classmethod
    def select_cars_by_id(cls,data):
        query = "SELECT * FROM cars LEFT JOIN car_owner ON cars.car_id = car_owner.cars_car_id LEFT JOIN users ON " \
                "user_id = car_owner.users_users_id WHERE cars.car_id = %(car_id)s;"
        results = MySQLConnection(db).query_db(query, data)

        car = cls(results[0])

        for row in results:
            if row['user_id'] == None:
                break
            data = {
                "user_id": row['users.user_id'],
                "first_name": row['first_name'],
                "last_name": row['last_name'],
                "email": row['email'],
                "password": row['password'],
                "created_at": row['created_at'],
                "updated_at": row['updated_at']
            }
            car.owners.append(be_users_model.Users(data))
        return car

    @classmethod
    def update_car(cls, data):
        query = "UPDATE cars SET model = %(model)s, make = %(make)s, year = %(year)s, " \
                "description = %(description)s, price = %(price)s WHERE car_id = %(car_id)s"
        results = MySQLConnection(db).query_db(query, data)
        return results

    @classmethod
    def was_sold(cls, data):
        query = "UPDATE cars SET was_sold = %(was_sold)s WHERE car_id = %(car_id)s;"
        results = MySQLConnection(db).query_db(query, data)
        return results

    @classmethod
    def sold_car(cls, data):
        query = "SELECT * FROM cars WHERE cars.car_id NOT IN ( SELECT cars FROM car_owner WHERE " \
                "users_user_id = %(user_id)s );"
        results = MySQLConnection(db).query_db(query, data)
        cars = []
        for row in results:
            cars.append(cls(row))
        return cars

    @classmethod
    def delete_car(cls,data):
        query = "DELETE FROM cars WHERE car_id = %(car_id);"
        results = MySQLConnection(db).query_db(query, db)
        return results

    @staticmethod
    def validate_car(car):
        is_valid = True

        if len(car['make']) < 1:
            flash("The make of the car must contain at least one characters", "car")
            is_valid = False
        if len(car['model']) < 3:
            flash("The model name must contain at least model characters", "car")
            is_valid = False
        if int(car['year']) < 0:
            flash("The year of the car must be greater than zero", "car")
            is_valid = False
        if int(car['price']) < 0:
            flash("The price of the car must be greater than zero", "car")
            is_valid = False
        if len(car['description']) < 3:
            flash("The description of the show must contain at least three characters", "car")
            is_valid = False
        return is_valid
