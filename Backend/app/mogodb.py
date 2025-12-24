import pymongo as pm


from pymongo import MongoClient, errors

def connectDB(uri="mongodb://localhost:27017", db_name=None):
    
    try:
        # Attempt connection with a timeout
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Try to ping the server to confirm connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")

        # Return the database if specified
        if db_name:
            return client[db_name]
        return client

    except errors.ConnectionFailure as e:
        print(f"❌ Could not connect to MongoDB: {e}")
        return None
    except errors.ConfigurationError as e:
        print(f"⚙️ Configuration Error: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")
        return None

# Example usage
client = connectDB()

