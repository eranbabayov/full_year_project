FROM mcr.microsoft.com/mssql/server:2022-latest

USER root

ENV ACCEPT_EULA=Y

COPY ./initialization.sql .
COPY ./entrypoint.sh .

RUN chmod +x ./entrypoint.sh
RUN mkdir -p /var/opt/mssql/backup

EXPOSE 1433

CMD [ "/bin/bash", "./entrypoint.sh" ]