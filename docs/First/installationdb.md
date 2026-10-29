sudo apt update
sudo apt install postgresql postgresql-client
pg_lsclusters          # doit afficher le cluster "online"
pg_isready             # doit répondre "accepting connections"
sudo ss -tlnp | grep 5432

sudo -u postgres psql

CREATE ROLE gestion_app LOGIN;
\password gestion_app
\q

sudo -u postgres psql -d gestion_personnel

GRANT USAGE ON SCHEMA public TO gestion_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO gestion_app;
REVOKE UPDATE, DELETE ON log FROM gestion_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO gestion_app;
\q

openssl rand -hex 32        # → SECRET_KEY
