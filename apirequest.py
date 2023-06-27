from flask import Flask, render_template, g
import http.client
import ssl
import psycopg2

app = Flask(__name__)

# Configure your PostgreSQL database connection details
db_host = 'apirds.cvthc7vdwzq3.us-east-1.rds.amazonaws.com'
db_port = '5432'
db_name = 'apirds'
db_user = 'postgres'
db_password = 'Opi2468!'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        # Create a connection to the PostgreSQL database
        db = g._database = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        # Close the database connection
        db.close()

def insert_data_into_db(data):
    conn = get_db()
    cursor = conn.cursor()

    # Define your SQL query to insert data into the database
    query = "INSERT INTO aapldata (apidata) VALUES (%s)"

    try:
        # Execute the SQL query for each data item
        for item in data:
            cursor.execute(query, (item,))

        # Commit the changes to the database
        conn.commit()
        print("Data inserted successfully into the database")
    except Exception as e:
        # Rollback the transaction in case of any error
        conn.rollback()
        print("Error inserting data into the database:", str(e))
    finally:
        # Close the cursor
        cursor.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api')
def api():
    context = ssl._create_unverified_context()
    conn = http.client.HTTPSConnection("stock-and-options-trading-data-provider.p.rapidapi.com", context=context)

    headers = {
        'X-RapidAPI-Proxy-Secret': "a755b180-f5a9-11e9-9f69-7bf51e845926",
        'X-RapidAPI-Key': "01802e6378msh6464091515065bcp13df9djsn0f20a84c4710",
        'X-RapidAPI-Host': "stock-and-options-trading-data-provider.p.rapidapi.com"
    }

    conn.request("GET", "/options/aapl", headers=headers)

    res = conn.getresponse()
    data = res.read()

    # Convert the data from API response to a list
    data_list = data.decode("utf-8").split(',')

    # Call the function to insert data into the database
    insert_data_into_db(data_list)

    return "Data pushed into the database"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
