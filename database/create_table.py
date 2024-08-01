import pandas as pd
import pymssql
import time
from dotenv import load_dotenv
import os
# Load the CSV file
#challenges_file_path = 'Challenges_Wexplanations.csv'
#Solutions_file_path = 'Solutions_Wexplanations.csv'
challenges_file_path = 'database/Challenges_Wexplanations.csv'
Solutions_file_path = 'database/Solutions_Wexplanations.csv'


challenges_df = pd.read_csv(challenges_file_path)
Solutions_df = pd.read_csv(Solutions_file_path)

# Drop rows with missing values
challenges_df_cleaned = challenges_df.dropna()
Solutions_df_cleaned = Solutions_df.dropna()
# Rename columns to remove spaces and ensure they are valid SQL column names
challenges_df_cleaned.columns = ['challengeID', 'category', 'text', 'problematic_row', 'explanation']
Solutions_df_cleaned.columns = ['solutionID', 'challengeID', 'text', 'correctness', 'explanation']
# Define connection details

load_dotenv()
password = os.getenv('MSSQL_SA_PASSWORD')

while True:
    try:
        conn = pymssql.connect(
            "127.0.0.1",
            "sa",
            password,
            "SecurityPerformance")
        break
    except pymssql.OperationalError:
        time.sleep(1)

cursor = conn.cursor()

# Insert data into the table
for index, row in challenges_df_cleaned.iterrows():
    insert_query = '''
    INSERT INTO Challenges (challengeID, category, text, problematic_row, explanation)
    VALUES (%d, %s, %s, %s, %s)
    '''
    cursor.execute(insert_query,
                   (row['challengeID'], row['category'], row['text'], row['problematic_row'], row['explanation']))

for index, row in Solutions_df_cleaned.iterrows():
    insert_query = '''
    INSERT INTO Solutions (solutionID, challengeID, text, correctness, explanation)
    VALUES (%d, %s, %s, %s, %s)
    '''
    cursor.execute(insert_query,
                   (row['solutionID'], row['challengeID'], row['text'], row['correctness'], row['explanation']))

conn.commit()

# Close the connection
conn.close()
print("Finished creating Challenges and Solutions tables")