#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER urlshortener WITH PASSWORD 'urlshortener';
    ALTER USER urlshortener WITH SUPERUSER;
    CREATE DATABASE urlshortener;
    GRANT ALL PRIVILEGES ON DATABASE urlshortener TO urlshortener;
    CREATE DATABASE urlshortener_test;
    GRANT ALL PRIVILEGES ON DATABASE urlshortener_test TO urlshortener;
EOSQL 