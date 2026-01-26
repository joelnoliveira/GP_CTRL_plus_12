from langfuse import get_client
from dotenv import load_dotenv

# Load .env to ensure we have credentials (though get_client might work without if we just want to inspect the object class, but better safe)
load_dotenv()

try:
    client = get_client()
    print("Methods/Attributes of Langfuse client:")
    print(dir(client))

    print("\nMethods/Attributes of client.api.datasets:")
    print(dir(client.api.datasets))
except Exception as e:
    print(f"Error: {e}")
