# Migrations

Tables are created automatically on backend startup via `Base.metadata.create_all`.
For production, initialise Alembic here (`alembic init .`) and point `sqlalchemy.url` at `DATABASE_URL`.
