import logging
import os
import time

from flask import Flask
from flask_pymongo import PyMongo
from pymongo import MongoClient
from pymongo.database import Database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/enginy")

MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds


def get_mongo_client() -> MongoClient:
    retries = 0
    while retries < MAX_RETRIES:
        try:
            client: MongoClient = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Trigger a command to test the connection
            client.admin.command("ismaster")
            logger.info("Successfully connected to MongoDB")
            return client
        except Exception as e:
            retries += 1
            logger.warning(
                f"Connection to MongoDB failed (attempt {retries}/{MAX_RETRIES}): {e}"
            )
            if retries < MAX_RETRIES:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)

    logger.error("Failed to connect to MongoDB after multiple attempts")
    raise ConnectionError("Could not connect to MongoDB")


mongo_client: MongoClient | None = None

try:
    mongo_client = get_mongo_client()
except ConnectionError:
    logger.error("Application startup failed - could not connect to MongoDB")

mongo = PyMongo()


def init_app(app: Flask) -> None:
    """Initialize the MongoDB connection with the Flask app."""
    app.config["MONGO_URI"] = MONGO_URI

    app.config["MONGO_AVAILABLE"] = mongo_client is not None

    if app.config["MONGO_AVAILABLE"]:
        mongo.init_app(app)

        try:
            with app.app_context():
                db = mongo.db
                if db is not None:
                    db.engine_parts.create_index([("user_id", 1)])
                    logger.info("MongoDB initialized successfully")
                else:
                    logger.error("MongoDB database is None")
                    app.config["MONGO_AVAILABLE"] = False
        except Exception as e:
            logger.error(f"Error during MongoDB initialization: {e}")
            app.config["MONGO_AVAILABLE"] = False
    else:
        logger.warning("MongoDB connection not available - running in limited mode")


def get_db() -> Database | None:
    """Get the MongoDB database instance."""
    if mongo_client is None:
        logger.warning("Database access attempted but MongoDB is not available")
        return None
    return mongo.db
