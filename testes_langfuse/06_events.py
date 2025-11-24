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

# Simple event
langfuse.create_event(
    name="user-login",
    metadata={"user_id": "user-123", "ip": "192.168.1.1"}
)
print("✅ Logged user-login event")

# Events within a trace
trace_id = langfuse.create_trace_id()
trace_context = {"trace_id": trace_id}

langfuse.create_event(
    trace_context=trace_context,
    name="page-view",
    metadata={"page": "/dashboard"}
)

time.sleep(1)

langfuse.create_event(
    trace_context=trace_context,
    name="button-click",
    metadata={"button": "generate-report"}
)

langfuse.create_event(
    trace_context=trace_context,
    name="api-call",
    metadata={"endpoint": "/api/reports", "status": 200}
)

print(f"✅ Logged 3 events in trace {trace_id}")

langfuse.flush()
print("📊 Check Langfuse UI for events!")
