from flask import Blueprint, render_template, url_for, request, session, redirect, flash
import psycopg2
import psycopg2.extras
from .config import db_name, user, password, host

view = Blueprint('view', __name__)


@view.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@view.route('/profile')
def profile():
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # условие проверки авторизации пользователя
    if 'logged_in' in session:
        cursor.execute('SELECT * FROM cinema_user WHERE login = %s',  [session['login']])
        account = cursor.fetchone()
        user_id = account[0]
        print(user_id)

        cursor.execute('SELECT film.title, seance.seance_date, seance.seance_time, seance.hall, '
                       'ticket.row, ticket.place, ticket.ticket_cost FROM ticket INNER JOIN seance '
                       'ON ticket.seance_id = seance.id INNER JOIN film ON seance.film_id = film.id'
                       ' WHERE ticket.user_id =%s', (user_id,))
        ticket = cursor.fetchall()
        ticket_len = len(ticket)

        return render_template('profile.html', account=account, ticket=ticket, ticket_len=ticket_len)
    # функция перенаправления
    return redirect(url_for('view.login'))


@view.route('/afisha', methods=['GET', 'POST'])
def afisha():
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute('SELECT title, release_date, countries_of_origin, genres, '
                   'age_limit, runtime, director, summary FROM film')
    film = cursor.fetchall()
    # Вычисление длинны массива
    film_len = len(film)

    return render_template('afisha.html', film=film, film_len=film_len)


@view.route('/about_cinema', methods=['GET', 'POST'])
def cinema():
    return render_template('cinema.html')


@view.route('/admin', methods=['GET', 'POST'])
def admin():
    return render_template('admin.html')


@view.route('/add_film', methods=['GET', 'POST'])
def add_film():
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("SELECT genre_name FROM genre")
    genre_name = cursor.fetchall()
    genre_name_len = len(genre_name)
    genre_name_dict = {}
    for i in range(genre_name_len):
        genre_name_dict[i+1] = genre_name[i][0]

    if request.method == "POST":
        film_id = request.form['id']
        title = request.form['title']
        release_date = request.form['release_date']
        countries_of_origin = request.form['countries_of_origin']
        genres = request.form['option_genre']
        age_limit = request.form['age_limit']
        runtime = request.form['runtime']
        director = request.form['director']
        summary = request.form['summary']

        cursor.execute('SELECT genre_name FROM genre WHERE id = %s', (genres,))
        film_genre = cursor.fetchone()

        cursor.execute('SELECT * FROM film WHERE id = %s', (film_id,))
        film = cursor.fetchone()
        print(film)

        if film:
            flash('Такой фильм уже есть в базе')
        else:
            cursor.execute(
                "INSERT INTO film (id, title, release_date, countries_of_origin, genres, age_limit, runtime, director, "
                "summary) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (film_id, title, release_date, countries_of_origin, film_genre, age_limit, runtime, director, summary))
            conn.commit()
            cursor.execute(
                "INSERT INTO film_genre (film_id, genre_id) VALUES (%s,%s)",
                (int(film_id), int(genres)))
            conn.commit()
            flash('Фильм добавлен')

    return render_template('add_film.html', genre_name_dict=genre_name_dict)


@view.route('/del_film', methods=['GET', 'POST'])
def del_film():
    if 'logged_in' not in session:
        redirect(url_for('home'))

    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("SELECT title FROM film")
    film_title = cursor.fetchall()
    film_len = len(film_title)
    film_dict = {}
    for i in range(film_len):
        film_dict[i + 1] = film_title[i][0]

    if request.method == 'POST':
        if request.form['option_delete'] == '0':
            pass
        else:
            option_delete = request.form['option_delete']
            option_delete_value = film_dict[int(option_delete)]
            cursor.execute("SELECT id FROM film WHERE title =%s", (option_delete_value,))
            film_id = cursor.fetchall()
            cursor.execute("DELETE FROM film_genre WHERE film_id =%s", film_id[0])
            conn.commit()
            cursor.execute("DELETE FROM film WHERE title =%s", (option_delete_value,))
            conn.commit()

            flash('Фильм удален')

        return redirect(url_for('view.del_film'))
    return render_template("del_film.html", film_dict=film_dict)


@view.route('/add_hall', methods=['GET', 'POST'])
def add_hall():
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == "POST":
        hall_id = request.form['id']
        place_count = request.form['place_count']
        row_num = request.form['row_num']
        place_num = request.form['place_num']

        cursor.execute('SELECT * FROM hall WHERE id = %s', (hall_id,))
        hall = cursor.fetchone()
        print(hall)

        if hall:
            flash('Информация про этот зал уже есть в базе')
        else:
            cursor.execute(
                "INSERT INTO hall (id, place_count, row_num, place_num) VALUES (%s,%s,%s,%s)",
                (hall_id, place_count, row_num, place_num))
            conn.commit()
            flash('Информация про этот зал добавлена')

    return render_template('add_hall.html')


@view.route('/add_seance', methods=['GET', 'POST'])
def add_seance():
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("SELECT title FROM film")
    title = cursor.fetchall()
    title_len = len(title)
    title_dict = {}
    for i in range(title_len):
        title_dict[i+1] = title[i][0]

    cursor.execute("SELECT id FROM hall")
    hall = cursor.fetchall()
    hall_len = len(hall)
    hall_dict = {}
    for i in range(hall_len):
        hall_dict[i + 1] = hall[i][0]

    if request.method == "POST":
        title = request.form['option_title']
        hall = request.form['option_hall']
        date = request.form['date']
        time = request.form['time']
        ticket_cost = request.form['ticket_cost']

        cursor.execute('SELECT * FROM seance WHERE hall = %s and seance_date = %s and seance_time = %s', (hall, date, time))
        seance = cursor.fetchone()
        print(seance)

        if seance:
            flash('Зал на это время уже занят')

        else:
            title_add = request.form['option_title']
            title_add_value = title_dict[int(title_add)]
            cursor.execute("SELECT id FROM film WHERE title =%s", (title_add_value,))
            film_id = cursor.fetchall()
            film_id = film_id[0]
            print(film_id)
            cursor.execute(
                "INSERT INTO seance (hall, seance_date, seance_time, film_id, ticket_cost) VALUES (%s,%s,%s,%s,%s)",
                (hall, date, time, film_id[0], ticket_cost))
            conn.commit()
            flash('Сеанс добавлен')

    return render_template('add_seance.html', title_dict=title_dict, hall_dict=hall_dict)


@view.route('/seance', methods=['GET', 'POST'])
def seance():
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute('SELECT film.title, seance.seance_date, seance.seance_time, seance.hall, seance.ticket_cost '
                   'FROM seance INNER JOIN film ON (film.id = seance.film_id)')
    seance = cursor.fetchall()
    # Вычисление длинны массива
    seance_len = len(seance)

    return render_template('seance.html', seance=seance, seance_len=seance_len)


@view.route('/add_ticket', methods=['GET', 'POST'])
def add_ticket():
    session.pop('ticket', None)
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute('SELECT * FROM seance')
    seance = cursor.fetchone()

    cursor.execute("SELECT title FROM film WHERE id IN (SELECT film_id FROM seance)")
    title = cursor.fetchall()
    title_len = len(title)
    title_dict = {}
    for i in range(title_len):
        title_dict[i+1] = title[i][0]

    cursor.execute("SELECT DISTINCT seance_date FROM seance")
    seance_date = cursor.fetchall()
    seance_date_len = len(seance_date)
    seance_date_dict = {}
    for i in range(seance_date_len):
        seance_date_dict[i + 1] = seance_date[i][0]

    cursor.execute("SELECT DISTINCT seance_time FROM seance")
    seance_time = cursor.fetchall()
    seance_time_len = len(seance_time)
    seance_time_dict = {}
    for i in range(seance_time_len):
        seance_time_dict[i + 1] = seance_time[i][0]

    cursor.execute("SELECT id FROM hall WHERE id in (SELECT hall FROM seance)")
    seance_hall = cursor.fetchall()
    seance_hall_len = len(seance_hall)
    seance_hall_dict = {}
    for i in range(seance_hall_len):
        seance_hall_dict[i + 1] = seance_hall[i][0]

    cursor.execute('SELECT DISTINCT MAX(row_num), MAX(place_num) FROM hall')
    place = cursor.fetchone()
    row_num = place[0]
    place_num = place[1]
    print(row_num, place_num)

    if request.method == "POST":
        title = request.form['option_title']
        date = request.form['option_date']
        time = request.form['option_time']
        hall = request.form['option_hall']
        row = request.form['option_row']
        place = request.form['option_place']

        title_value = title_dict[int(title)]
        cursor.execute("SELECT id FROM film WHERE title =%s", (title_value,))
        film_id = cursor.fetchall()
        film_id = film_id[0]
        print(film_id)
        date_value = seance_date_dict[int(date)]
        time_value = seance_time_dict[int(time)]
        print(date_value)
        print(time_value)
        hall_value = seance_hall_dict[int(hall)]

        cursor.execute('SELECT * FROM seance WHERE (film_id = %s and hall = %s and seance_date = %s and'
                       ' seance_time = %s)', (film_id[0], hall_value, date_value, time_value))
        seance = cursor.fetchone()
        print(seance)

        if seance:
            seance_id = seance[0]
            print(seance_id)
            cursor.execute('SELECT row, place FROM ticket WHERE seance_id = %s', (seance_id,))
            seance_place = cursor.fetchone()
            print(seance_place)

            if seance_place is None:
                cursor.execute('SELECT id FROM cinema_user WHERE login = %s', [session['login']])
                user_id = cursor.fetchone()
                print(user_id)
                cursor.execute('SELECT ticket_cost FROM seance WHERE id = %s', (seance_id,))
                ticket_cost = cursor.fetchone()
                print(ticket_cost)
                cursor.execute('INSERT INTO ticket (seance_id, place, ticket_cost, user_id, row) VALUES (%s,%s,%s,%s,'
                               '%s)', (seance_id, place, ticket_cost[0], user_id[0], row))
                conn.commit()
                flash('Вы успешно приобрели билет!')

            else:
                flash('Это место уже занято')

        else:
            flash('Такого сеанса не существует, проверьте корректность введенных данных')

    return render_template('add_ticket.html', title_dict=title_dict, seance_date_dict=seance_date_dict,
                           seance_time_dict=seance_time_dict, seance_hall_dict=seance_hall_dict, seance=seance,
                           row_num=row_num, place_num=place_num)
