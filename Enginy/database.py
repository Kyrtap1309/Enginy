import os
from pymongo import MongoClient
from flask_pymongo import PyMongo


MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/enginy")

mongo_client = MongoClient(MONGO_URI)

mongo = PyMongo()

def init_app(app):
    """Initialize the MongoDB connection with the Flask app."""
    app.config["MONGO_URI"] = MONGO_URI
    mongo.init_app(app)

    with app.app_context():
        mongo.db.engine_parts.create_index([('user_id', 1)])

def get_db():
    """Get the MongoDB database instance."""
    return mongo.db