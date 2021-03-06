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


@view.route('/hall')
def hall():
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute('SELECT * FROM hall')
    hall_inf = cursor.fetchall()
    hall_len = len(hall_inf)

    return render_template('hall.html', hall_inf=hall_inf, hall_len=hall_len)


@view.route('/akzii')
def akzii():
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute('SELECT * FROM akzii')
    akzii = cursor.fetchall()
    akzii_len = len(akzii)

    return render_template('akzii.html', akzii=akzii, akzii_len=akzii_len)


@view.route('/add_akzii', methods=['GET', 'POST'])
def add_akzii():
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == "POST":
        name = request.form['name']
        discription = request.form['discription']

        cursor.execute(
            "INSERT INTO akzii (name, discription) VALUES (%s,%s)", (name, discription, ))
        conn.commit()
        flash('Информация об акции добавлена')

    return render_template('add_akzii.html')


@view.route('/del_akzii', methods=['GET', 'POST'])
def del_akzii():
    if 'logged_in' not in session:
        redirect(url_for('home'))

    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("SELECT name FROM akzii")
    akzii = cursor.fetchall()
    hakzii_len = len(akzii)
    akzii_dict = {}
    for i in range(hakzii_len):
        akzii_dict[i + 1] = akzii[i][0]

    if request.method == 'POST':
        if request.form['option_delete'] == '0':
            pass
        else:
            option_delete = request.form['option_delete']
            option_delete_value = akzii_dict[int(option_delete)]
            cursor.execute("DELETE FROM akzii WHERE name =%s", (option_delete_value,))
            conn.commit()

            flash('Акция удалена')

        return redirect(url_for('view.del_akzii'))
    return render_template("del_akzii.html", akzii_dict=akzii_dict)


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
            cursor.execute("SELECT film_id FROM seance WHERE film_id =%s", film_id[0])
            seance = cursor.fetchall()

            if seance:
                flash('Нельзя удалить фильм, пока он в прокате')
            else:
                cursor.execute("DELETE FROM film_genre WHERE film_id =%s", film_id[0])
                conn.commit()
                cursor.execute("DELETE FROM film WHERE title =%s", (option_delete_value,))
                conn.commit()

                flash('Фильм удален')

            return redirect(url_for('view.del_film'))
    return render_template("del_film.html", film_dict=film_dict)


@view.route('/del_hall', methods=['GET', 'POST'])
def del_hall():
    if 'logged_in' not in session:
        redirect(url_for('home'))

    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("SELECT id FROM hall")
    hall_id = cursor.fetchall()
    hall_id_len = len(hall_id)
    hall_id_dict = {}
    for i in range(hall_id_len):
        hall_id_dict[i + 1] = hall_id[i][0]

    if request.method == 'POST':
        if request.form['option_delete'] == '0':
            pass
        else:
            option_delete = request.form['option_delete']
            option_delete_value = hall_id_dict[int(option_delete)]

            cursor.execute("SELECT hall FROM seance WHERE hall =%s", (option_delete_value,))
            hall = cursor.fetchall()

            if hall:
                flash('Нельзя удалить зал, пока там идут сеансы')
            else:
                cursor.execute("DELETE FROM hall WHERE id =%s", (option_delete_value,))
                conn.commit()

                flash('Зал удален')

            return redirect(url_for('view.del_hall'))
    return render_template("del_hall.html", hall_id_dict=hall_id_dict)


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

    if request.method == "POST":
        session.pop('seance_id', None)
        title = request.form['option_title']
        date = request.form['option_date']
        time = request.form['option_time']
        hall = request.form['option_hall']

        title_value = title_dict[int(title)]
        cursor.execute("SELECT id FROM film WHERE title =%s", (title_value,))
        film_id = cursor.fetchall()
        film_id = film_id[0]
        print(film_id)
        date_value = seance_date_dict[int(date)]
        time_value = seance_time_dict[int(time)]
        time_value_str = str(time_value)
        print(date_value)
        print(time_value)
        hall_value = seance_hall_dict[int(hall)]
        print(hall_value)

        cursor.execute('SELECT * FROM seance WHERE (film_id = %s and hall = %s and seance_date = %s and'
                       ' seance_time = %s)', (film_id[0], hall_value, date_value, time_value))
        seance = cursor.fetchone()
        print(seance)

        if seance:
            seance_id = seance[0]
            print(seance_id)
            cursor.execute('SELECT id FROM cinema_user WHERE login = %s', [session['login']])
            user_id = cursor.fetchone()
            print(user_id)
            cursor.execute('SELECT ticket_cost FROM seance WHERE id = %s', (seance_id,))
            ticket_cost = cursor.fetchone()
            print(ticket_cost)
            # cursor.execute(
            #         'INSERT INTO ticket (seance_id, ticket_cost, user_id) VALUES (%s,%s,'
            #         '%s)', (seance_id, ticket_cost[0], user_id[0],))
            # conn.commit()
            session['seance_id'] = seance_id
            session['ticket_cost'] = ticket_cost[0]
            session['user_id'] = user_id
            session['title'] = title_value
            session['date'] = date_value
            session['time'] = time_value_str
            session['hall'] = hall_value
            session.modified = True
            print(session['seance_id'])
            print(session['ticket_cost'])
            print(session['user_id'])
            print(session['title'])
            print(session['date'])
            print(session['hall'])
            flash('Вы успешно почти приобрели билет!')
            return redirect(url_for('view.add_ticket2'))

        else:
            flash('Такого сеанса не существует, проверьте корректность введенных данных')

    return render_template('add_ticket.html', title_dict=title_dict, seance_date_dict=seance_date_dict,
                           seance_time_dict=seance_time_dict, seance_hall_dict=seance_hall_dict, seance=seance)


@view.route('/add_ticket2', methods=['GET', 'POST'])
def add_ticket2():
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT row_num FROM hall WHERE id IN (SELECT hall FROM seance WHERE id = %s)",
                   (session['seance_id'],))
    place_row = cursor.fetchall()
    row_num = place_row[0][0]
    print(row_num)
    cursor.execute("SELECT place_num FROM hall WHERE id IN (SELECT hall FROM seance WHERE id = %s)",
                   (session['seance_id'],))
    place_row = cursor.fetchall()
    place_num = place_row[0][0]
    print(place_num)

    cursor.execute("SELECT row, place FROM ticket WHERE seance_id = %s",
                   (session['seance_id'],))
    zplace = cursor.fetchall()
    zplace_len = len(zplace)

    if request.method == "POST":
        row = request.form['option_row']
        place = request.form['option_place']

        cursor.execute('SELECT row FROM ticket WHERE seance_id = %s', (session['seance_id'],))
        seance_row = cursor.fetchone()
        print("row", seance_row)
        cursor.execute('SELECT place FROM ticket WHERE seance_id = %s', (session['seance_id'],))
        seance_place = cursor.fetchone()
        print("place", seance_place)

        if (seance_row is None and seance_place is None) or (seance_row is not None and seance_place is None)\
                        or (seance_row is None and seance_place is not None):
            seance_row_x = 0
            seance_place_x = 0
            cursor.execute('SELECT id FROM cinema_user WHERE login = %s', [session['login']])
            user_id = cursor.fetchone()
            print(user_id)
            cursor.execute('SELECT ticket_cost FROM seance WHERE id = %s', (session['seance_id'],))
            ticket_cost = cursor.fetchone()
            print(ticket_cost)
            cursor.execute(
                    'INSERT INTO ticket (seance_id, place, ticket_cost, user_id, row) VALUES (%s,%s,%s,%s,'
                    '%s)', (session['seance_id'], place, ticket_cost[0], user_id[0], row))
            conn.commit()

        else:
            seance_row_x = seance_row.count(int(row))
            seance_place_x = seance_place.count(int(place))
            print(seance_place_x, seance_row_x)

            if seance_row_x == 0 and seance_place_x == 0:
                cursor.execute('SELECT id FROM cinema_user WHERE login = %s', [session['login']])
                user_id = cursor.fetchone()
                print(user_id)
                cursor.execute('SELECT ticket_cost FROM seance WHERE id = %s', (session['seance_id'],))
                ticket_cost = cursor.fetchone()
                print(ticket_cost)
                cursor.execute(
                        'INSERT INTO ticket (seance_id, place, ticket_cost, user_id, row) VALUES (%s,%s,%s,%s,'
                        '%s)', (session['seance_id'], place, ticket_cost[0], user_id[0], row))
                conn.commit()
                flash('Вы успешно приобрели билет!')

            else:
                flash('Это место уже занято')

    return render_template("add_ticket2.html", row_num=row_num, place_num=place_num,  zplace=zplace, zplace_len=zplace_len)


@view.route('/del_seance', methods=['GET', 'POST'])
def del_seance():
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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

    if request.method == "POST":
        title = request.form['option_title']
        date = request.form['option_date']
        time = request.form['option_time']
        hall = request.form['option_hall']

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
            cursor.execute('DELETE FROM ticket WHERE seance_id = %s', (seance_id,))
            conn.commit()
            cursor.execute('DELETE FROM seance WHERE (film_id = %s and hall = %s and seance_date = %s and'
                           ' seance_time = %s)', (film_id[0], hall_value, date_value, time_value))
            conn.commit()
            flash('Вы успешно удалили сеанс!')

        else:
            flash('Такого сеанса не существует, проверьте корректность введенных данных')

    return render_template('del_seance.html', title_dict=title_dict, seance_date_dict=seance_date_dict,
                           seance_time_dict=seance_time_dict, seance_hall_dict=seance_hall_dict)