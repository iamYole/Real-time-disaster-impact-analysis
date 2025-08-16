import requests
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv('API_URL')

insert_query = """
    INSERT INTO disaster (
                disasterNumber,
                declarationDate,
                incidentType,
                projectSize,
                applicationTitle,
                applicantId,
                damageCategoryCode,
                county,
                projectAmount,
                damageCategoryDescrip,      
                lastRefresh)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

def extract_data():
    response = requests.get(URL)
    response.raise_for_status()  # ✅ fail fast if API request fails
    return response.json()['PublicAssistanceFundedProjectsDetails']

def main():
    try:
        conn = psycopg2.connect(
            host=os.getenv('HOST', 'localhost'),   # fallback to localhost
            port=os.getenv('PORT', 5432),
            database=os.getenv('DATABASE'),
            user=os.getenv('USERNAME'),
            password=os.getenv('PASSWORD')
        )
    except Exception as e:
        print(f"❌ Error connecting to Postgres: {e}")

    try:
        cur = conn.cursor()

        # Create table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS disaster (
                disasterNumber INT,
                declarationDate TIMESTAMPTZ,
                incidentType TEXT,
                projectSize TEXT,
                applicationTitle TEXT,
                applicantId TEXT,
                damageCategoryCode TEXT,
                county TEXT,
                projectAmount DECIMAL(10,2),
                damageCategoryDescrip TEXT,      
                lastRefresh TIMESTAMPTZ
            )
        """)
        conn.commit()

        # Extract + transform data
        data = extract_data()
        postgres_data = [
            (row['disasterNumber'], row['declarationDate'], row['incidentType'],
             row['projectSize'], row['applicationTitle'], row['applicantId'],
             row['damageCategoryCode'], row['county'], row['projectAmount'],
             row['damageCategoryDescrip'], row['lastRefresh'])
            for row in data
        ]

   
        # Insert
        cur.executemany(insert_query, postgres_data)
        conn.commit()

        print(f"{len(postgres_data)} records loaded successfully!")

    except Exception as e:
        print(f"❌ Error executing query: {e}")

    finally:
        # Close connections safely
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
