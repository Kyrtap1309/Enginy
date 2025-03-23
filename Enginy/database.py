import logging
import os
import time

from flask_pymongo import PyMongo
from pymongo import MongoClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get MongoDB URI from environment variable or use a default local URI
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/enginy")

# Maximum retry attempts for MongoDB connection
MAX_RETRIES = 5
RETRY_DELAY = 2  # seconds


# Initialize MongoDB client with retry logic
def get_mongo_client():
    retries = 0
    while retries < MAX_RETRIES:
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
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


try:
    mongo_client = get_mongo_client()
except ConnectionError:
    logger.error("Application startup failed - could not connect to MongoDB")
    mongo_client = None

mongo = PyMongo()


def init_app(app):
    """Initialize the MongoDB connection with the Flask app."""
    app.config["MONGO_URI"] = MONGO_URI

    # Add connection status to application config
    app.config["MONGO_AVAILABLE"] = mongo_client is not None

    if app.config["MONGO_AVAILABLE"]:
        mongo.init_app(app)

        try:
            with app.app_context():
                mongo.db.engine_parts.create_index([("user_id", 1)])
                logger.info("MongoDB initialized successfully")
        except Exception as e:
            logger.error(f"Error during MongoDB initialization: {e}")
            app.config["MONGO_AVAILABLE"] = False
    else:
        logger.warning("MongoDB connection not available - running in limited mode")


def get_db():
    """Get the MongoDB database instance."""
    if mongo_client is None:
        logger.warning("Database access attempted but MongoDB is not available")
    return mongo.db
