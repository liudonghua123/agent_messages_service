import os
import time
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Query, APIRouter, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from dotenv import load_dotenv

from database import get_db, Chat
from models import ChatCreate, ChatResponse, SearchRequest, SearchCondition, StatusResponse
# Import MCP functions directly instead of mounting
from mcp_server import mcp

load_dotenv()

# Create ASGI app from MCP server
mcp_app = mcp.http_app(path='/mcp')

# Create FastAPI app
app = FastAPI(
    title="Agent Messages Service",
    description="MCP and REST API service for managing agent chat messages",
    version="1.0.0",
    lifespan=mcp_app.lifespan
)

# Create API router
api_router = APIRouter(prefix="/api")

# Track startup time
startup_time = time.time()

# REST API endpoints
@api_router.get("/status", response_model=StatusResponse)
async def get_status(db: Session = Depends(get_db)):
    """Get application status and statistics"""
    uptime_seconds = time.time() - startup_time
    uptime_str = f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m {int(uptime_seconds % 60)}s"
    
    total_chats = db.query(Chat).count()
    
    return StatusResponse(
        status="running",
        uptime=uptime_str,
        version="1.0.0",
        database_type=os.getenv("DATABASE_TYPE", "sqlite"),
        total_chats=total_chats
    )

def parse_special_datetime_filter(value: str) -> datetime:
    """Parse special datetime filters like last_5_minutes, last_2_hours"""
    pattern = r'^last_(\d+)_(minutes|hours)$'
    match = re.match(pattern, value.lower())
    
    if not match:
        raise ValueError(f"Invalid datetime filter format: {value}")
    
    amount = int(match.group(1))
    unit = match.group(2)
    
    now = datetime.now()
    if unit == 'minutes':
        return now - timedelta(minutes=amount)
    elif unit == 'hours':
        return now - timedelta(hours=amount)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")

def parse_query_params(request: Request) -> Dict[str, Any]:
    """Parse query parameters into filters"""
    filters = {}
    pagination = {'pagenum': 1, 'pagesize': 10}
    
    for key, value in request.query_params.items():
        if key in ['pagenum', 'pagesize']:
            pagination[key] = int(value)
        elif '-' in key:
            # Handle field-operator format
            parts = key.split('-', 1)
            field = parts[0]
            operator = parts[1]
            
            if field not in filters:
                filters[field] = []
            
            # Handle between operator specially
            if operator == 'between':
                values = value.split(',')
                if len(values) != 2:
                    raise HTTPException(status_code=400, detail=f"Between operator requires two values separated by comma for {key}")
                filters[field].append({
                    'operator': operator,
                    'value': values[0].strip(),
                    'value2': values[1].strip()
                })
            else:
                filters[field].append({
                    'operator': operator,
                    'value': value
                })
        else:
            # Handle simple field=value format
            if key not in filters:
                filters[key] = []
            filters[key].append({
                'operator': 'eq',
                'value': value
            })
    
    return filters, pagination

def apply_filter_to_query(query, field: str, filter_conditions: List[Dict], db_model):
    """Apply filter conditions to SQLAlchemy query"""
    field_attr = getattr(db_model, field, None)
    if not field_attr:
        raise HTTPException(status_code=400, detail=f"Invalid field: {field}")
    
    for condition in filter_conditions:
        operator = condition['operator']
        value = condition['value']
        if value == "false" or value == "true":
            value = 1 if value == "true" else 0

        # Handle datetime field special filters
        if field == 'datetime' and isinstance(value, str):
            if value.startswith('last_'):
                try:
                    value = parse_special_datetime_filter(value)
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=str(e))
            else:
                # Try to parse as ISO datetime
                try:
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid datetime format: {value}")
        
        # Handle value2 for between operator
        value2 = condition.get('value2')
        if value2 and field == 'datetime' and isinstance(value2, str):
            if value2.startswith('last_'):
                try:
                    value2 = parse_special_datetime_filter(value2)
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=str(e))
            else:
                try:
                    value2 = datetime.fromisoformat(value2.replace('Z', '+00:00'))
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid datetime format: {value2}")
        
        # Apply filter based on operator
        if operator == "eq":
            query = query.filter(field_attr == value)
        elif operator == "ne":
            query = query.filter(field_attr != value)
        elif operator == "gt":
            query = query.filter(field_attr > value)
        elif operator == "ge":
            query = query.filter(field_attr >= value)
        elif operator == "lt":
            query = query.filter(field_attr < value)
        elif operator == "le":
            query = query.filter(field_attr <= value)
        elif operator == "like":
            query = query.filter(field_attr.like(f"%{value}%"))
        elif operator == "between":
            if value2 is None:
                raise HTTPException(status_code=400, detail="value2 is required for between operator")
            query = query.filter(and_(field_attr >= value, field_attr <= value2))
        else:
            raise HTTPException(status_code=400, detail=f"Invalid operator: {operator}")
    
    return query

@api_router.get("/chats", response_model=List[ChatResponse])
async def get_chats(request: Request, db: Session = Depends(get_db)):
    """Get chat records with flexible filtering
    
    Supports query parameters in formats:
    - Simple: field=value (e.g., user=john)
    - With operator: field-operator=value (e.g., process_time-gt=100)
    - Between: field-between=value1,value2 (e.g., datetime-between=2023-01-01,2023-12-31)
    - Special datetime: datetime-gt=last_5_minutes, datetime-between=last_2_hours,last_1_hours
    
    Pagination: pagenum=1, pagesize=10 (defaults)
    """
    try:
        filters, pagination = parse_query_params(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    query = db.query(Chat)
    
    # Apply filters
    for field, filter_conditions in filters.items():
        query = apply_filter_to_query(query, field, filter_conditions, Chat)
    
    # Pagination
    pagenum = pagination.get('pagenum', 1)
    pagesize = pagination.get('pagesize', 10)
    
    # Validate pagination
    if pagenum < 1:
        pagenum = 1
    if pagesize < 1 or pagesize > 100:
        pagesize = 10
    
    offset = (pagenum - 1) * pagesize
    chats = query.order_by(Chat.datetime.desc()).offset(offset).limit(pagesize).all()
    
    return chats

@api_router.post("/chats", response_model=List[ChatResponse])
async def create_chats(chats: List[ChatCreate], db: Session = Depends(get_db)):
    """Create multiple chat records"""
    db_chats = []
    for chat_data in chats:
        db_chat = Chat(**chat_data.dict())
        db.add(db_chat)
        db_chats.append(db_chat)
    
    db.commit()
    for db_chat in db_chats:
        db.refresh(db_chat)
    
    return db_chats

@api_router.delete("/chats")
async def delete_chats(
    id: Optional[int] = Query(None),
    ids: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Delete chat records by ID or IDs"""
    if not id and not ids:
        raise HTTPException(status_code=400, detail="Either 'id' or 'ids' parameter is required")
    
    if id:
        chat = db.query(Chat).filter(Chat.id == id).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        db.delete(chat)
        deleted_count = 1
    elif ids:
        try:
            id_list = [int(x.strip()) for x in ids.split(",")]
            deleted_count = db.query(Chat).filter(Chat.id.in_(id_list)).delete(synchronize_session=False)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid IDs format")
    
    db.commit()
    return {"message": f"Successfully deleted {deleted_count} chat record(s)"}

# Include API router
app.include_router(api_router)


# Mount MCP app
app.mount("/ai", mcp_app)

# Serve static files (frontend) at /static
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(static_dir, "index.html"))
    app.mount("/", StaticFiles(directory=static_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run("main:app", host=host, port=port, reload=debug)