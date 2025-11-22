"""
Test 6: Events and Observability
Log custom events for user actions and system behavior
"""
from config import *
from langfuse import Langfuse
import os
import time

os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_HOST"] = LANGFUSE_HOST

langfuse = Langfuse()

print("📡 Testing events/observability...")

# Events within a trace
trace = langfuse.trace(name="user-activity")

trace.event(
    name="user-login",
    metadata={"user_id": "user-123", "ip": "192.168.1.1"}
)
print("✅ Logged user-login event")

trace.event(
    name="page-view",
    metadata={"page": "/dashboard"}
)

time.sleep(1)

trace.event(
    name="button-click",
    metadata={"button": "generate-report"}
)

trace.event(
    name="api-call",
    metadata={"endpoint": "/api/reports", "status": 200}
)

print(f"✅ Logged 4 events in trace {trace.id}")

langfuse.flush()
print("📊 Check Langfuse UI for events!")
