from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
from .database import engine

# Create a MetaData instance
metadata = MetaData()

# Create the automap base
Base = automap_base(metadata=metadata)

# Reflection will happen when first accessed
_reflected = False

def reflect_tables():
    """Reflect the existing database tables"""
    global _reflected
    if not _reflected:
        Base.prepare(autoload_with=engine)
        _reflected = True

def get_models():
    """Get reflected models (call this after tables are created)"""
    reflect_tables()
    return Base.classes
