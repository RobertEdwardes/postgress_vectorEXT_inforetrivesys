FROM ankane/pgvector

ENV POSTGRES_DB=your-db-name
ENV POSTGRES_USER=your-db-user
ENV POSTGRES_PASSWORD=your-db-password

EXPOSE 5432

RUN echo "host all all 0.0.0.0/0 md5" >> /var/lib/postgresql/data/pg_hba.conf
RUN echo "listen_addresses = '*'" >> /var/lib/postgresql/data/postgresql.conf
