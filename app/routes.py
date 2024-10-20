import requests, json
from flask import current_app, jsonify, render_template, current_app as app, request, session, redirect, flash, url_for
import re
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor

def db_conn():
    try:
        config = current_app.config
        conn = psycopg2.connect(
            database=config['DATABASE_NAME'],
            user=config['DATABASE_USER'],
            password=config['DATABASE_PASSWORD'],
            host=config['DATABASE_HOST'],
            port=config['DATABASE_PORT']
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@company\.com$'
    return re.match(pattern, email)

def is_valid_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{7,}$'
    return re.match(pattern, password)


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not is_valid_email(email):
            error = "Email must be in the format letters and numbers with domain @company.com'"
            return render_template('create_account.html', error=error)
        if not is_valid_password(password):
            error = "Password must contain at least one uppercase letter, one lowercase letter, one number, and be at least 7 characters long"
            return render_template('create_account.html', error=error)


        hashed_password = generate_password_hash(password, method='sha256')

        conn = db_conn()
        if conn is not None:
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
                conn.commit()
                cur.close()
                flash('Account created successfully!', 'success')
                return redirect(url_for('login')) 
            except Exception as e:
                flash(f'Error creating account: {e}', 'danger')
                return redirect(url_for('create_account'))
            finally:
                conn.close()
        else:
            flash('Database connection failed!', 'danger')
            return redirect(url_for('create_account'))

    return render_template('create_account.html')


@app.route('/login', methods=['GET', 'POST'])
@app.route('/')
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = db_conn()
        if conn is not None:
            try:
                cur = conn.cursor()
                cur.execute("SELECT email, password FROM users WHERE email = %s", (email,))
                user = cur.fetchone()
                if user and check_password_hash(user[1], password):
                    session['email'] = email
                    return redirect(url_for('index'))
                else:
                    error = "Invalid email or password"
                    return render_template('login.html', error=error)
            except Exception as e:
                error = f"Error logging in: {e}"
                return render_template('login.html', error=error)
            finally:
                cur.close()
                conn.close()
        else:
            error = "Database connection failed"
            return render_template('login.html', error=error)
    return render_template('login.html')




@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/users')
def get_users():
    conn = db_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()

    cur.close()
    conn.close()
    
    return jsonify(users)


currencies = [
    {'name': 'US Dollar', 'code': 'USD'},
    {'name': 'Euro', 'code': 'EUR'},
    {'name': 'British Pound', 'code': 'GBP'},
    {'name': 'Ukrainian hryvnia', 'code': 'UAH'},
    {'name': 'Polish zloty', 'code': 'PLN'},
]

@app.route('/currency_convert', methods=['GET', 'POST'])
def convert_currency():
    if request.method == 'POST':
        from_currency = request.form['from_currency']
        to_currency = request.form['to_currency']
        amount = float(request.form['amount'])

        url = "https://currency-conversion-and-exchange-rates.p.rapidapi.com/convert"
        querystring = {"from": from_currency, "to": to_currency, "amount": amount}

        headers = {
            "x-rapidapi-key": "818814693dmsh15b4c01d27d115ap1fd441jsn141093198a76",
            "x-rapidapi-host": "currency-conversion-and-exchange-rates.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        date = data.get('date', [])
        result_amount = data.get('result', [])
        
        return render_template('convert_currency.html', 
                            currencies=currencies,
                            conversion_result=True,
                            date=date,
                            start_amount=amount,
                            from_currency=from_currency,
                            to_currency=to_currency,
                            result_amount=result_amount
                            )
    else:
        return render_template('convert_currency.html', currencies=currencies)


@app.route('/exchange_rate', methods=['GET', 'POST'])
def exchange_rate():    
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        base_currency = request.form['base_currency']
        to_currency = request.form['to_currency']


        url = "https://currency-conversion-and-exchange-rates.p.rapidapi.com/timeseries"
        querystring = {"start_date": start_date,"end_date": end_date, "base": base_currency}

        headers = {
            "x-rapidapi-key": "818814693dmsh15b4c01d27d115ap1fd441jsn141093198a76",
            "x-rapidapi-host": "currency-conversion-and-exchange-rates.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()


        filtered_data = {}
        for date in data['rates'].keys():
            filtered_rates = {currency: rate for currency, rate in data['rates'][date].items() if currency == to_currency}
            filtered_data[date] = filtered_rates


        return render_template('exchange_rate.html', filtered_data=filtered_data, date=date, data=data, currencies=currencies, conversion_result=True,)
    
    else:
        return render_template('exchange_rate.html', currencies=currencies)

