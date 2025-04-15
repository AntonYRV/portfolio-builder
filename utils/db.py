import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Absolute path to the base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Full path to the SQLite database file
DATABASE_PATH = os.path.join(BASE_DIR, "moex_data.db")

# SQLite database URL for SQLAlchemy connection
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create an SQLAlchemy engine to connect to the database
# The "check_same_thread" parameter allows the connection to be shared across threads
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session factory that is bound to the engine
# This will be used to interact with the database in a transaction-safe way
SessionLocal = sessionmaker(bind=engine)

