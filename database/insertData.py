import pymssql
import os
import pandas as pd
import json

def sqlToJson():
    password = '<YourStrong@Passw0rd>'
    conn = pymssql.connect("127.0.0.1", "sa", password, "SecurityPerformance")
    query = f'SELECT * FROM challenges'
    df = pd.read_sql(query, conn)
    json_data = df.to_json(orient='records', indent=4)
    with open('database/jsonChallenges.json', 'w') as jf:
        jf.write(json_data)



def insertDatan():
    password = '<YourStrong@Passw0rd>'
    conn = pymssql.connect("127.0.0.1", "sa", password, "SecurityPerformance")
    # insert chalenge file data
    chalengeFilePath = "C:/Users/matan/OneDrive/Documents/Computer_Scince/HIT/2024(B)/full_year_project-main/database/challanges.csv"

    cursor = conn.cursor()
    df = pd.read_csv(chalengeFilePath)
    itr = df.iterrows()
    i = 1
    for index, row in df.iterrows():

        with conn.cursor(as_dict=True) as cursor:
            # Start a transaction
            conn.autocommit(False)
            cursor.execute(
                "INSERT INTO challenges (challengeID, category, text, problematic_row) VALUES (%d, %s, %s, %d)",
                (int(row['challangeID']), row['category'], row['text'], int(row['problematic_row'])))
            
            # Commit the transaction
            conn.commit()
                

        print("DONE******")



    
        

