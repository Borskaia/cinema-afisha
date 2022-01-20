from flask import Blueprint, render_template, url_for, request, session, redirect, flash
import psycopg2
import psycopg2.extras
from werkzeug.security import generate_password_hash, check_password_hash
from .config import db_name, user, password, host

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    session.permanent = False
    session.modified = True
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == "POST" and 'login' in request.form:
        user_password = request.form['user_password']
        user_password1 = request.form['user_password1']
        user_name = request.form['user_name']
        login = request.form['login']
        date_of_birth = request.form['date']

        _hashed_password = generate_password_hash(user_password)
        print(_hashed_password)

        cursor.execute('SELECT * FROM cinema_user WHERE login = %s', (login,))
        account = cursor.fetchone()
        print(account)

        # If account exists show error and validation checks
        if account:
            flash('Аккаунт уже существует')
        elif not user_password:
            flash('Заполните все формы!')
        elif user_password != user_password1:
            flash('Пароли не совпадают')
        else:

            # Account doesn't exist and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO cinema_user (login, user_password, user_name, date_of_birth) VALUES (%s,%s,%s,%s)",
                           (login, _hashed_password, user_name, date_of_birth))
            conn.commit()
            flash('Вы успешно зарегистрировались!')

    elif request.method == 'POST':

        # Form is empty... (no POST data)
        flash('Заполните все формы!')

        # Show registration form with message (if any)
    return render_template('register.html')


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    session.permanent = False

    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # user submitted form
    if request.method == 'POST' and 'login' in request.form and 'user_password' in request.form:
        login = request.form['login']
        user_password = request.form['user_password']

        # check if exist in database
        cursor.execute('SELECT * FROM cinema_user WHERE login = %s', (login,))
        account = cursor.fetchone()
        print(account)

        if account:
            password_rs = account['user_password']
            print(password_rs)

            if check_password_hash(password_rs, user_password):
                session['logged_in'] = True
                session.modified = True
                print(session.get('logged_in'))
                session['login'] = account['login']
                print(session.get('login'))
                adm = account['isadmin']
                print(adm)
                user_name = account['user_name']
                if adm:
                    session['isAdmin'] = True
                    flash('Вы успешно вошли в аккаунт, Админ! ')
                    return redirect(url_for('view.admin'))
                else:
                    session['isAdmin'] = False
                    flash('Вы успешно вошли в аккаунт')
                    return redirect(url_for('view.home'))

            else:
                flash('Неправильный пароль')

        else:
            flash('Неправильный логин или пароль')

    return render_template('login.html'), session


@auth.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('isAdmin', None)
    session.pop('seance_id', None)
    session.pop('ticket_cost', None)
    session.pop('user_id', None)
    session.pop('title', None)
    session.pop('date', None)
    session.pop('time', None)
    session.pop('hall', None)
    flash('Вы успешно вышли из аккаунта')
    return redirect(url_for('view.home'))
