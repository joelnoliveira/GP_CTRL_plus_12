import time
import uuid
import requests
import os
from dotenv import load_dotenv
from langfuse import Langfuse

load_dotenv()

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")

def test_simple_rw():
    print("🚀 Starting Simple Read/Write Test...")

    # 1. Initialize Client
    langfuse = Langfuse()

    # 2. Create a Trace (Write)
    # In v3 SDK, we use start_span or similar, but let's check if we can create a trace directly.
    # It seems 'trace' method is gone. We can use 'start_span' or 'start_as_current_span'.
    # But wait, we want a root trace.
    
    trace_id = uuid.uuid4().hex
    print(f"📝 Creating Trace with ID: {trace_id}")
    
    # Using start_span to create a root span (which acts as a trace)
    # Or maybe just use observe() decorator in a real app.
    # Let's try start_span with no parent.
    
    span = langfuse.start_span(
        name="simple-rw-test",
        trace_context={"trace_id": trace_id},
        metadata={"test": "true", "type": "read-write"}
    )
    
    # Add a child span
    # In v3, we use start_span on the client again, passing the parent context, 
    # OR if 'span' object has a method to create child. 
    # Actually, LangfuseSpan usually doesn't have .span(). 
    # We should use langfuse.start_span with parent_id from the previous span.
    
    # But wait, if we use the context manager it's easier.
    # Let's just end the root span for this simple test.
    
    # child = span.span(
    #    name="write-operation",
    #    input={"data": "hello world"},
    #    output={"result": "success"}
    # )
    # child.end()
    span.end()
    
    # 3. Flush to ensure data is sent
    print("💾 Flushing data...")
    langfuse.flush()
    
    # 4. Wait for async processing
    print("⏳ Waiting 2 seconds for ingestion...")
    time.sleep(2)

    # 5. Read back the trace (Read)
    print(f"🔍 Attempting to read trace {trace_id} from API...")
    
    # Try the GET endpoint. 
    # Note: In Langfuse v3, reading traces usually happens via the authenticated API.
    # We'll try the standard endpoint structure.
    
    url = f"{LANGFUSE_HOST}/api/public/traces/{trace_id}"
    
    try:
        response = requests.get(
            url,
            auth=(LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY)
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Trace found!")
            print(f"   Name: {data.get('name')}")
            print(f"   ID: {data.get('id')}")
            print("🎉 Read/Write Test Passed!")
        elif response.status_code == 404:
             print("⚠️ Trace not found (404). It might take longer to ingest or the endpoint is different.")
             # Fallback check for health
             print(f"Checking health: {requests.get(f'{LANGFUSE_HOST}/api/public/health').status_code}")
        elif response.status_code == 405:
             print("⚠️ Method Not Allowed (405). Trying alternative endpoint...")
             # Try without /public/
             url = f"{LANGFUSE_HOST}/api/traces/{trace_id}"
             response = requests.get(url, auth=(LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY))
             if response.status_code == 200:
                print("✅ Trace found (via /api/traces)!")
                print(f"   ID: {response.json().get('id')}")
             else:
                print(f"❌ Failed on alternative endpoint: {response.status_code}")
        else:
            print(f"❌ Error fetching trace: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Exception during read: {e}")

if __name__ == "__main__":
    test_simple_rw()
