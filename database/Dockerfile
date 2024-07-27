FROM mcr.microsoft.com/mssql/rhel/server:2022-CU12-rhel-8.7

USER root

ENV ACCEPT_EULA=Y

COPY ./initialization.sql .
COPY ./entrypoint.sh .
COPY ./create_table.py .
COPY ./requirements.txt .
COPY ./Challenges_Wexplanations.csv .
COPY ./Solutions_Wexplanations.csv .

# Install Python and pip
RUN yum -y install python3 python3-pip

# Install Python dependencies
RUN pip3 install -r requirements.txt

RUN chmod +x ./entrypoint.sh
RUN mkdir -p /var/opt/mssql/backup

EXPOSE 1433

CMD [ "/bin/bash", "./entrypoint.sh" ]
