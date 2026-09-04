FROM mysql:8.4

COPY scripts/sql/* /docker-entrypoint-initdb.d/

EXPOSE 3306

HEALTHCHECK --interval=5s --timeout=3s --start-period=20s --retries=12 \
    CMD mysqladmin ping --host=127.0.0.1 --user=root --password="$MYSQL_ROOT_PASSWORD" --silent