"""
Article Eater v19.0 - WebSocket Real-Time Updates
Live updates for job queue, progress, and notifications
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Set, Optional
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts updates
    """
    
    def __init__(self):
        # Active connections: user_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
        # All connections (for broadcasting to everyone)
        self.all_connections: Set[WebSocket] = set()
        
        # Connection metadata
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Add to all connections
        self.all_connections.add(websocket)
        
        # Add to user-specific connections if user_id provided
        if user_id:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)
        
        # Store connection metadata
        self.connection_info[websocket] = {
            "user_id": user_id,
            "connected_at": datetime.now().isoformat(),
            "message_count": 0
        }
        
        logger.info(f"WebSocket connected: user={user_id}, total={len(self.all_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to Article Eater real-time updates"
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        # Get user_id before removing
        info = self.connection_info.get(websocket, {})
        user_id = info.get("user_id")
        
        # Remove from all connections
        self.all_connections.discard(websocket)
        
        # Remove from user-specific connections
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Remove metadata
        if websocket in self.connection_info:
            del self.connection_info[websocket]
        
        logger.info(f"WebSocket disconnected: user={user_id}, total={len(self.all_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific client"""
        try:
            await websocket.send_json(message)
            
            # Update message count
            if websocket in self.connection_info:
                self.connection_info[websocket]["message_count"] += 1
                
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def send_to_user(self, message: dict, user_id: str):
        """Send a message to all connections of a specific user"""
        if user_id not in self.active_connections:
            return
        
        disconnected = set()
        
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_json(message)
                
                if websocket in self.connection_info:
                    self.connection_info[websocket]["message_count"] += 1
                    
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients"""
        disconnected = set()
        
        for websocket in self.all_connections:
            try:
                await websocket.send_json(message)
                
                if websocket in self.connection_info:
                    self.connection_info[websocket]["message_count"] += 1
                    
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected:
            self.disconnect(websocket)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.all_connections),
            "users_connected": len(self.active_connections),
            "connections_by_user": {
                user_id: len(connections)
                for user_id, connections in self.active_connections.items()
            }
        }


# Global connection manager instance
manager = ConnectionManager()


# ============================================================================
# MESSAGE TYPES
# ============================================================================

async def notify_job_status(job_id: str, status: str, user_id: Optional[str] = None, 
                           progress: Optional[int] = None, error: Optional[str] = None):
    """Notify about job status change"""
    message = {
        "type": "job_status",
        "job_id": job_id,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    
    if progress is not None:
        message["progress"] = progress
    
    if error:
        message["error"] = error
    
    if user_id:
        await manager.send_to_user(message, user_id)
    else:
        await manager.broadcast(message)


async def notify_job_progress(job_id: str, progress: int, message: str, user_id: Optional[str] = None):
    """Notify about job progress"""
    data = {
        "type": "job_progress",
        "job_id": job_id,
        "progress": progress,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if user_id:
        await manager.send_to_user(data, user_id)
    else:
        await manager.broadcast(data)


async def notify_new_article(article_id: str, title: str, user_id: Optional[str] = None):
    """Notify about new article added"""
    message = {
        "type": "new_article",
        "article_id": article_id,
        "title": title,
        "timestamp": datetime.now().isoformat()
    }
    
    if user_id:
        await manager.send_to_user(message, user_id)
    else:
        await manager.broadcast(message)


async def notify_new_rule(rule_id: str, rule: str, confidence: float, user_id: Optional[str] = None):
    """Notify about new rule synthesized"""
    message = {
        "type": "new_rule",
        "rule_id": rule_id,
        "rule": rule,
        "confidence": confidence,
        "timestamp": datetime.now().isoformat()
    }
    
    if user_id:
        await manager.send_to_user(message, user_id)
    else:
        await manager.broadcast(message)


async def notify_system_message(message_text: str, level: str = "info"):
    """Broadcast system message to all users"""
    message = {
        "type": "system_message",
        "level": level,
        "message": message_text,
        "timestamp": datetime.now().isoformat()
    }
    
    await manager.broadcast(message)


# ============================================================================
# HEARTBEAT & KEEPALIVE
# ============================================================================

async def heartbeat_task():
    """Send periodic heartbeat to keep connections alive"""
    while True:
        await asyncio.sleep(30)  # Every 30 seconds
        
        if manager.all_connections:
            await manager.broadcast({
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat(),
                "connections": len(manager.all_connections)
            })


# ============================================================================
# CLIENT-SIDE JAVASCRIPT EXAMPLE
# ============================================================================

CLIENT_EXAMPLE = """
// Frontend WebSocket client example

class ArticleEaterWS {
    constructor(url = 'ws://localhost:8000/ws') {
        this.url = url;
        this.ws = null;
        this.reconnectDelay = 1000;
        this.maxReconnectDelay = 30000;
        this.handlers = {};
    }
    
    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('✓ WebSocket connected');
            this.reconnectDelay = 1000;
            this.onConnectionChange(true);
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('✗ WebSocket disconnected');
            this.onConnectionChange(false);
            this.reconnect();
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    reconnect() {
        setTimeout(() => {
            console.log('Reconnecting...');
            this.connect();
            this.reconnectDelay = Math.min(
                this.reconnectDelay * 2,
                this.maxReconnectDelay
            );
        }, this.reconnectDelay);
    }
    
    handleMessage(data) {
        const handler = this.handlers[data.type];
        if (handler) {
            handler(data);
        } else {
            console.log('Unhandled message type:', data.type, data);
        }
    }
    
    on(type, handler) {
        this.handlers[type] = handler;
    }
    
    onConnectionChange(connected) {
        // Override this in your app
        console.log('Connection status:', connected);
    }
}

// Usage example:
const ws = new ArticleEaterWS();

ws.on('job_status', (data) => {
    console.log('Job status:', data.job_id, data.status);
    // Update UI
});

ws.on('job_progress', (data) => {
    console.log('Job progress:', data.job_id, data.progress);
    // Update progress bar
});

ws.on('new_article', (data) => {
    console.log('New article:', data.title);
    // Add to article list
});

ws.on('new_rule', (data) => {
    console.log('New rule:', data.rule);
    // Add to rules list
});

ws.connect();
"""


if __name__ == "__main__":
    """Print client example"""
    print("WebSocket Real-Time Updates - Client Example:")
    print("=" * 60)
    print(CLIENT_EXAMPLE)
