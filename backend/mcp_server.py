from fastmcp import FastMCP
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db, Chat
from models import ChatCreate
import json

# Create MCP server
mcp = FastMCP("Agent Messages Service")

@mcp.tool()
def add_chats(chats_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Add multiple chat records to the database.
    
    Args:
        chats_data: List of chat records with fields: session, question, answer, datetime, user, fullfill
    
    Returns:
        Dictionary with success status and count of added records
    """
    try:
        db = next(get_db())
        added_count = 0
        
        for chat_data in chats_data:
            # Parse datetime if it's a string
            if isinstance(chat_data.get('datetime'), str):
                chat_data['datetime'] = datetime.fromisoformat(chat_data['datetime'].replace('Z', '+00:00'))
            
            chat = Chat(
                session=chat_data['session'],
                question=chat_data['question'],
                answer=chat_data['answer'],
                datetime=chat_data['datetime'],
                user=chat_data['user'],
                fullfill=chat_data.get('fullfill', False),
                process_time=chat_data.get('process_time', 0)
            )
            db.add(chat)
            added_count += 1
        
        db.commit()
        return {
            "success": True,
            "message": f"Successfully added {added_count} chat records",
            "count": added_count
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Error adding chats: {str(e)}",
            "count": 0
        }
    finally:
        db.close()

@mcp.tool()
def search_chats(search_params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Search chat records based on various criteria.
    
    Args:
        search_params: Dictionary with search parameters like user, session, fullfill, etc.
    
    Returns:
        Dictionary with search results
    """
    try:
        db = next(get_db())
        query = db.query(Chat)
        
        if search_params:
            if 'user' in search_params:
                query = query.filter(Chat.user == search_params['user'])
            if 'session' in search_params:
                query = query.filter(Chat.session == search_params['session'])
            if 'fullfill' in search_params:
                query = query.filter(Chat.fullfill == search_params['fullfill'])
            if 'datetime_from' in search_params:
                query = query.filter(Chat.datetime >= search_params['datetime_from'])
            if 'datetime_to' in search_params:
                query = query.filter(Chat.datetime <= search_params['datetime_to'])
        
        results = query.order_by(Chat.datetime.desc()).limit(100).all()
        
        return {
            "success": True,
            "count": len(results),
            "data": [
                {
                    "id": chat.id,
                    "session": chat.session,
                    "question": chat.question,
                    "answer": chat.answer,
                    "datetime": chat.datetime.isoformat(),
                    "user": chat.user,
                    "fullfill": chat.fullfill,
                    "process_time": chat.process_time
                }
                for chat in results
            ]
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error searching chats: {str(e)}",
            "data": []
        }
    finally:
        db.close()

@mcp.tool()
def get_chat_stats() -> Dict[str, Any]:
    """
    Get statistics about chat records.
    
    Returns:
        Dictionary with various statistics
    """
    try:
        db = next(get_db())
        
        total_chats = db.query(Chat).count()
        fulfilled_chats = db.query(Chat).filter(Chat.fullfill == True).count()
        unique_users = db.query(Chat.user).distinct().count()
        unique_sessions = db.query(Chat.session).distinct().count()
        
        return {
            "success": True,
            "stats": {
                "total_chats": total_chats,
                "fulfilled_chats": fulfilled_chats,
                "unfulfilled_chats": total_chats - fulfilled_chats,
                "unique_users": unique_users,
                "unique_sessions": unique_sessions,
                "fulfillment_rate": round((fulfilled_chats / total_chats * 100) if total_chats > 0 else 0, 2)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting stats: {str(e)}",
            "stats": {}
        }
    finally:
        db.close()