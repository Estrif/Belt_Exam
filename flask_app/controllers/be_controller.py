from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.be_users_model import Users
from flask_app.models.be_cars_model import Cars
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)


# Users

@app.route('/login_page')
def index():
    print("Hello")
    return render_template("be_index.html")


@app.route('/register/user', methods=['POST'])
def register():
    if not Users.validate_register(request.form):
        return redirect('/login_page')

    data = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email": request.form['email'],
        "password": bcrypt.generate_password_hash(request.form['password'])
    }

    user_id = Users.save_users(data)
    session['user_id'] = user_id

    return redirect('/dashboard')


@app.route('/login', methods=['POST'])
def login():
    user_in_db = Users.get_user_by_email(request.form)
    if not user_in_db:
        flash("Invalid Email/Password", "login")
        return redirect('/login_page')
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        flash("Invalid Email/Password", "login")
        return redirect('/login_page')

    session['user_id'] = user_in_db.user_id
    return redirect('/dashboard')


# Shows

@app.route('/dashboard')
def cars_page():
    if 'user_id' not in session:
        return redirect('login_page')

    data = {
        'user_id': session['user_id']
    }

    user = Users.get_user_by_id(data)

    cars = Cars.get_all_cars()

    return render_template("be_cars_page.html", all_cars=cars, user=user)


@app.route('/new')
def new_car_page():
    if 'user_id' not in session:
        return redirect('login_page')

    data = {
        'user_id': session['user_id']
    }

    user = Users.get_user_by_id(data)

    return render_template("be_cars_new_page.html", user=user)


@app.route('/create', methods=['POST'])
def create_car():
    print(session['user_id'])
    if 'user_id' not in session:
        return redirect('login_page')

    if not Cars.validate_car(request.form):
        return redirect('/new')
    data = {
        "model": request.form['model'],
        "make": request.form['make'],
        "year": request.form['year'],
        "price": request.form['price'],
        "description": request.form['description'],
        "seller_id": session['user_id']
    }

    print("Hello")
    Cars.save_car(data)
    print("Hello after save")
    return redirect('/dashboard')


@app.route('/show/<int:car_id>')
def view_car(car_id):
    if 'user_id' not in session:
        return redirect('login_page')

    data = {
        "car_id": car_id
    }
    user_data = {
        "user_id": session['user_id']
    }
    car = Cars.select_cars_by_id(data)
    user = Users.get_user_by_id(user_data)

    return render_template("be_view_car.html", one_car=car, user=user)


@app.route('/edit/<int:car_id>')
def edit_car_page(car_id):
    if 'user_id' not in session:
        return redirect('login_page')

    data = {
        "car_id": car_id
    }
    user_data = {
        "user_id": session['user_id']
    }

    cars = Cars.get_car_by_id(data)
    user = Users.get_user_by_id(user_data)
    return render_template('be_edit_car_page.html', one_car=cars, user=user)


@app.route('/update/<int:car_id>', methods=['GET', 'POST'])
def update_car(car_id):
    if 'user_id' not in session:
        return redirect('login_page')
    if not Cars.validate_car(request.form):
        return redirect(f"/update/{car_id}")

    data = {
        "car_id": request.form['car_id'],
        "model": request.form['model'],
        "make": request.form['make'],
        "year": request.form['year'],
        "price": request.form['price'],
        "description": request.form['description']
    }
    Cars.update_car(data)
    return redirect('/dashboard')


@app.route('/delete/<int:car_id>')
def delete_car(car_id):
    if 'user_id' not in session:
        return redirect('login_page')

    data = {
        "car_id": car_id
    }

    Cars.delete_car(data)

    return redirect('/dashboard')


@app.route('/purchase/<int:car_id>')
def purchase_car(car_id):
    data = {
        'user_id': session['user_id'],
        'car_id': car_id
    }
    Users.purchase_cars(data)

    was_sold = 1
    car_data = {
        'car_id': car_id,
        'was_sold': was_sold
    }
    Cars.was_sold(car_data)
    return redirect(f"/show/{session['user_id']}/cars")


@app.route('/show/<int:user_id>/cars')
def show_my_purchases(user_id):
    if 'user_id' not in session:
        return redirect('login_page')

    data = {
        "user_id": user_id
    }

    user = Users.get_user_by_id(data)
    return render_template("be_show_purchases.html", user=user)
