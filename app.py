from flask import Flask, jsonify
from flask import render_template, request, redirect, url_for, current_app
import uuid
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor
import json

from contextlib import contextmanager
from collections import Counter
import os

pool = None

app = Flask(__name__)


option_mapping = {
    'option1': 1,
    'option2': 2,
    'option3': 3,
    'option4': 4,
    'option5': 5,
    'option6': 6,
    'option7': 7
}

familiarity_mapping = {
    1: "Not at all familiar",
    2: "Slightly familiar",
    3: "Somewhat familiar",
    4: "Moderately familiar",
    5: "Familiar",
    6: "Very familiar",
    7: "Extremely familiar"
}

number_of_artworks_mapping = {
    1: "None",
    2: "1-5 artworks",
    3: "6-10 artworks",
    4: "11-20 artworks",
    5: "21-50 artworks",
    6: "51-100 artworks",
    7: "More than 100 artworks"
}


@app.before_request
def setup():
    global pool
    DATABASE_URL = os.environ['DATABASE_URL']
    current_app.logger.info(f"Creating db connection pool")
    pool = ThreadedConnectionPool(1, 100, dsn = DATABASE_URL, sslmode='require')

@contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)

@contextmanager
def get_db_cursor(commit = False):
    with get_db_connection() as connection:
        cursor = connection.cursor(cursor_factory=DictCursor)
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/survey')
def accept():
    return render_template('survey.html')

@app.route('/decline')
def decline():
    return render_template('decline.html')

@app.route('/thanks', methods=['POST', 'GET'])
def thanks():
    if request.method == 'POST':
        data = {
            "uuid": str(uuid.uuid4()),
            "name": request.form.get('userInput', 'None'),
            "familiarity": option_mapping.get(request.form.get('options', 'None'), 0),
            "number_of_artworks": option_mapping.get(request.form.get('selectionOption', 'None'), 0),
            "intended_use": request.form.get('conditionalTextarea', 'None')
        }
        json_data = json.dumps(data)
        insert_query = """
        INSERT INTO responses(uuid, name, familiarity, number_of_artworks, intended_use)
        VALUES (%s, %s, %s, %s, %s)
        """

        with get_db_cursor(True) as cur:
            current_app.logger.info("Test run")
            cur.execute(insert_query, (
                data['uuid'],
                data['name'],
                data['familiarity'],
                data['number_of_artworks'],
                data['intended_use']
            ))

        return render_template('thanks.html')
    

    else:
        return redirect(url_for('index'))
    
@app.route('/hi', methods=['GET'])
def hello_world():
  user_name = request.args.get("userName", "unknown")
  return render_template('main.html', user=user_name) 

@app.route('/api/results', methods=['GET'])
def get_results():
    with get_db_cursor(True) as cur:

        # Adjust the SELECT query to match your table name and columns
        reverse_order = request.args.get('reverse', 'false').lower() == 'true'
        if reverse_order:
            cur.execute("SELECT * FROM responses ORDER BY created_at DESC")
        else:
            cur.execute("SELECT * FROM responses ORDER BY created_at ASC")

        # Fetch all rows from the last executed query
        records = cur.fetchall()

        # Define column names as they appear in your database table
        column_names = [desc[0] for desc in cur.description]

        # Convert query results to a list of dictionaries
        results = []
        for row in records:
            row_dict = dict(zip(column_names, row))
            if 'familiarity' in row_dict:
                row_dict['familiarity'] = familiarity_mapping.get(row_dict['familiarity'], "Unknown")
            if 'number_of_artworks' in row_dict:
                row_dict['number_of_artworks'] = number_of_artworks_mapping.get(row_dict['number_of_artworks'], "Unknown range")
        
            results.append(row_dict)

        return jsonify(results)
    
def get_summary_data():
    data = {'familiarity': {}, 'number_of_artworks': {}}
    with get_db_cursor(True) as cur:
        # Query to count occurrences of each familiarity level
        cur.execute("SELECT familiarity, COUNT(*) FROM responses GROUP BY familiarity")
        for description in familiarity_mapping.values():
            data['familiarity'][description] = 0
        for row in cur.fetchall():
            # Assuming row[0] is the familiarity level, row[1] is the count
            data['familiarity'][familiarity_mapping.get(row[0], "Unknown")] = row[1]

        for description in number_of_artworks_mapping.values():
            data['number_of_artworks'][description] = 0
        # Query to count occurrences of each number_of_artworks category
        cur.execute("SELECT number_of_artworks, COUNT(*) FROM responses GROUP BY number_of_artworks")
        for row in cur.fetchall():
            # Assuming row[0] is the artworks category, row[1] is the count
            data['number_of_artworks'][number_of_artworks_mapping.get(row[0], "Unknown")] = row[1]

    return data

def get_time_series_data():
    dates = []
    counts = []
    with get_db_cursor(True) as cur:
        cur.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM responses
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """)
        for row in cur.fetchall():
            dates.append(row[0].isoformat())  # Convert date to string if necessary
            counts.append(row[1])
    return dates, counts

def get_name_data():
    with get_db_cursor(True) as cur:
        cur.execute("""
                    SELECT name FROM responses ORDER BY created_at DESC
                    """) 
        names = [row[0] for row in cur.fetchall()]
    name_counts = Counter(names)
    
    # Convert the counts to the desired format
    data = [{"x": name, "value": count} for name, count in name_counts.items()]
    
    return data

def get_intended_use_data():
    with get_db_cursor(True) as cur:
        cur.execute("SELECT intended_use FROM responses ORDER BY created_at DESC")  # Consider adding a LIMIT here
        intended_uses = [row[0] for row in cur.fetchall()]
    return intended_uses
    

@app.route('/admin/summary')
def admin_summary():
    summary_data = get_summary_data()
    dates, counts = get_time_series_data()
    names = get_name_data()
    intended_uses = get_intended_use_data()
    print(summary_data)
    return render_template('admin_summary.html', summary_data=summary_data, dates=dates, counts=counts, names = names, intended_uses = intended_uses)