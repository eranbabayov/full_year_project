#!/bin/bash
set -e

# Start SQL Server
/opt/mssql/bin/sqlservr &

echo "Waiting for SQL Server to start..."
until /opt/mssql-tools/bin/sqlcmd -S 127.0.0.1 -U SA -P ${MSSQL_SA_PASSWORD} -Q "SELECT 1;" > /dev/null 2>&1; do
    sleep 1
sleep 3
done

echo "SQL Server is now ready."

# Check if the database has been initialized
if /opt/mssql-tools/bin/sqlcmd -S 127.0.0.1 -U SA -P ${MSSQL_SA_PASSWORD} -Q "SELECT name FROM sys.databases WHERE name = 'SecurityPerformance';" | grep -q "SecurityPerformance"; then
  echo "Database has already been initialized."
else
  echo "Database has not been initialized. Initializing database..."
    /opt/mssql-tools/bin/sqlcmd -S 127.0.0.1 -U SA -P ${MSSQL_SA_PASSWORD} -d master -i initialization.sql
    echo "Running Python script..."
    python3 create_table.py

fi
# Print the tables created in the SecurityPerformance database
echo "Tables created in the SecurityPerformance database:"
/opt/mssql-tools/bin/sqlcmd -S 127.0.0.1 -U SA -P ${MSSQL_SA_PASSWORD} -d SecurityPerformance -Q "SELECT name FROM sys.tables;"

# Keep the container running
tail -f /dev/null