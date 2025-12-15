import os
from flask import Flask, render_template, request, jsonify
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

app = Flask(__name__)

# Database connection parameters
DB_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME)
    conn.cursor_factory = psycopg2.extras.DictCursor
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/zoeken', methods=['GET'])
def zoeken():
    telefoonnummer = request.args.get('telefoonnummer', '')
    facebookid = request.args.get('facebookid', '')
    voornaam = request.args.get('voornaam', '')
    achternaam = request.args.get('achternaam', '')
    geslacht = request.args.get('geslacht', '')
    plaatsnaam = request.args.get('plaatsnaam', '')
    status = request.args.get('status', '')
    bedrijfsnaam = request.args.get('bedrijfsnaam', '')
    return performsearch(telefoonnummer,facebookid,voornaam,achternaam,geslacht,plaatsnaam,status,bedrijfsnaam)

@app.route('/search', methods=['POST'])
def search():
    # Get search parameters from form
    telefoonnummer = request.form.get('telefoonnummer', '')
    facebookid = request.form.get('facebookid', '')
    voornaam = request.form.get('voornaam', '')
    achternaam = request.form.get('achternaam', '')
    geslacht = request.form.get('geslacht', '')
    plaatsnaam = request.form.get('plaatsnaam', '')
    status = request.form.get('status', '')
    bedrijfsnaam = request.form.get('bedrijfsnaam', '')
    return performsearch(telefoonnummer,facebookid,voornaam,achternaam,geslacht,plaatsnaam,status,bedrijfsnaam)
    
def performsearch(telefoonnummer,facebookid,voornaam,achternaam,geslacht,plaatsnaam,status,bedrijfsnaam):
    # Build query dynamically based on provided parameters
    query = "SELECT * FROM profiles WHERE 1=1"
    params = []
    
    if telefoonnummer:
        query += " AND telefoonnummer ILIKE %s"
        params.append(f"%{telefoonnummer}%")
    
    if facebookid:
        query += " AND facebookid ILIKE %s"
        params.append(f"%{facebookid}%")
    
    if voornaam:
        query += " AND voornaam ILIKE %s"
        params.append(f"%{voornaam}%")
    
    if achternaam:
        query += " AND achternaam ILIKE %s"
        params.append(f"%{achternaam}%")
    
    if geslacht:
        query += " AND geslacht ILIKE %s"
        params.append(f"%{geslacht}%")
    
    if plaatsnaam:
        query += " AND (plaatsnaam ILIKE %s OR geboorteplaats ILIKE %s)"
        params.append(f"%{plaatsnaam}%")
        params.append(f"%{plaatsnaam}%")
    
    if status:
        query += " AND status ILIKE %s"
        params.append(f"%{status}%")
    
    if bedrijfsnaam:
        query += " AND bedrijfsnaam ILIKE %s"
        params.append(f"%{bedrijfsnaam}%")
    
    # Add limit to prevent overwhelming results
    # query += " LIMIT 100"
    
    # Execute query
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    results = cur.fetchall()
    
    # Convert results to list of dictionaries
    columns = [desc[0] for desc in cur.description]
    results_list = [dict(zip(columns, row)) for row in results]
    
    cur.close()
    conn.close()
    
    return render_template('index.html', results=results_list, search_params=request.form)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
