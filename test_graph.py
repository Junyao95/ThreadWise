from graph_client import GraphClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def test_graph_connection():
    print("Testing Graph API connection...")
    
    # Check if required environment variables are set
    required_vars = ["AZURE_CLIENT_ID", "AZURE_TENANT_ID", "AZURE_CLIENT_SECRET"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("Please check your .env file.")
        return False
    
    try:
        client = GraphClient()
        token = client.get_access_token()
        print(f"✅ Successfully acquired access token!")
        print(f"   Token starts with: {token[:50]}...")
        print(f"   Token length: {len(token)} characters")
        return True
    except Exception as e:
        print(f"❌ Failed to get token: {e}")
        return False

if __name__ == "__main__":
    test_graph_connection()
