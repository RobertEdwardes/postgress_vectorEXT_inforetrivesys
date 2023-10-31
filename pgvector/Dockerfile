FROM ankane/pgvector

ENV POSTGRES_DB=db_replace
ENV POSTGRES_USER=root_replace
ENV POSTGRES_PASSWORD=root_replace

EXPOSE 5432

RUN echo "host all all 0.0.0.0/0 md5" >> /var/lib/postgresql/data/pg_hba.conf
RUN echo "listen_addresses = '*'" >> /var/lib/postgresql/data/postgresql.conf
