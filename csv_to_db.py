import os
import csv
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Database connection parameters
DB_URL = os.getenv("DATABASE_URL")

def parse_belgium_line(line):
    """Parse a line from Belgium.txt which has special comma handling for plaatsnaam."""
    parts = []
    in_quotes = False
    current_part = ""
    
    for char in line:
        if char == ',' and not in_quotes:
            parts.append(current_part)
            current_part = ""
        else:
            # Check for comma followed by space in plaatsnaam
            if char == ',' and ' ' in current_part:
                in_quotes = True
            current_part += char
    
    # Add the last part
    if current_part:
        parts.append(current_part)
    
    # Ensure we have the right number of fields
    if len(parts) < 8:
        parts.extend([""] * (8 - len(parts)))
    
    # Map to the correct field order (no geboorteplaats in Belgium data)
    return {
        'telefoonnummer': parts[0],
        'facebookid': parts[1],
        'voornaam': parts[2],
        'achternaam': parts[3],
        'geslacht': parts[4],
        'plaatsnaam': parts[5],
        'geboorteplaats': '',  # Not present in Belgium data
        'status': parts[6],
        'bedrijfsnaam': parts[7]
    }

def process_netherlands_file(filename):
    """Process Netherlands files with colon-separated values."""
    records = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(':')
            if len(parts) >= 9:
                record = {
                    'telefoonnummer': parts[0],
                    'facebookid': parts[1],
                    'voornaam': parts[2],
                    'achternaam': parts[3],
                    'geslacht': parts[4],
                    'plaatsnaam': parts[5],
                    'geboorteplaats': parts[6],
                    'status': parts[7],
                    'bedrijfsnaam': parts[8]
                }
                records.append(record)
    return records

def process_belgium_file(filename):
    """Process Belgium file with comma-separated values and special handling for plaatsnaam."""
    records = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            record = parse_belgium_line(line.strip())
            records.append(record)
    return records

def insert_records_to_db(records, batch_size=1000):
    """Insert records into the database in batches."""
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    total_records = len(records)
    for i in range(0, total_records, batch_size):
        batch = records[i:i+batch_size]
        values = [(
            record['telefoonnummer'],
            record['facebookid'],
            record['voornaam'],
            record['achternaam'],
            record['geslacht'],
            record['plaatsnaam'],
            record['geboorteplaats'],
            record['status'],
            record['bedrijfsnaam']
        ) for record in batch]
        
        query = """
        INSERT INTO profiles (
            telefoonnummer, facebookid, voornaam, achternaam, 
            geslacht, plaatsnaam, geboorteplaats, status, bedrijfsnaam
        ) VALUES %s
        """
        execute_values(cursor, query, values)
        
        conn.commit()
        print(f"Inserted {i + len(batch)} of {total_records} records")
    
    cursor.close()
    conn.close()

def main():
    # Process Netherlands files
    records = []
    records.extend(process_netherlands_file('Netherlands 01.txt'))
    records.extend(process_netherlands_file('Netherlands 02.txt'))
    
    # Process Belgium file
    records.extend(process_belgium_file('Belgium.txt'))
    
    # Insert all records to database
    insert_records_to_db(records)
    print(f"Total records processed: {len(records)}")

if __name__ == "__main__":
    main()