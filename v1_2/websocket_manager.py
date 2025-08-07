#!/usr/bin/env python3
"""
WebSocket Manager for integrating with main application
Provides thread-safe WebSocket sender management
"""

import threading
import asyncio
import logging
import time
from websocket_sender import WebSocketSender

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Thread-safe WebSocket Manager for background operation"""
    
    def __init__(self):
        self.sender = None
        self.sender_thread = None
        self.loop = None
        self.running = False
        self.lock = threading.Lock()
        
    def _run_sender_loop(self):
        """Run WebSocket sender in background thread"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.loop = loop
            
            # Create and run sender
            self.sender = WebSocketSender()
            
            logger.info("WebSocket sender thread started")
            loop.run_until_complete(self.sender.run())
            
        except Exception as e:
            logger.error(f"WebSocket sender thread failed: {e}")
        finally:
            logger.info("WebSocket sender thread stopped")
            self.running = False
            if self.loop and not self.loop.is_closed():
                self.loop.close()
    
    def start_sender(self):
        """Start WebSocket sender in background thread"""
        with self.lock:
            if self.running:
                logger.info("WebSocket sender is already running")
                return True
            
            try:
                self.running = True
                self.sender_thread = threading.Thread(
                    target=self._run_sender_loop,
                    daemon=True,
                    name="WebSocketSender"
                )
                self.sender_thread.start()
                
                # Give it a moment to start
                time.sleep(1)
                
                logger.info("WebSocket sender started successfully")
                return True
                
            except Exception as e:
                logger.error(f"Failed to start WebSocket sender: {e}")
                self.running = False
                return False
    
    def stop_sender(self):
        """Stop WebSocket sender"""
        with self.lock:
            if not self.running:
                logger.info("WebSocket sender is not running")
                return True
            
            try:
                # Signal the sender to stop
                if self.sender:
                    self.sender.stop()
                
                # Stop the event loop
                if self.loop and not self.loop.is_closed():
                    self.loop.call_soon_threadsafe(self.loop.stop)
                
                # Wait for thread to finish
                if self.sender_thread and self.sender_thread.is_alive():
                    self.sender_thread.join(timeout=10)
                
                self.running = False
                self.sender = None
                self.sender_thread = None
                self.loop = None
                
                logger.info("WebSocket sender stopped successfully")
                return True
                
            except Exception as e:
                logger.error(f"Error stopping WebSocket sender: {e}")
                return False
    
    def is_running(self):
        """Check if WebSocket sender is running"""
        with self.lock:
            return (self.running and 
                    self.sender_thread and 
                    self.sender_thread.is_alive())
    
    def get_status(self):
        """Get WebSocket sender status"""
        with self.lock:
            return {
                'running': self.is_running(),
                'thread_alive': self.sender_thread.is_alive() if self.sender_thread else False,
                'sender_active': self.sender.running if self.sender else False
            }
    
    def restart_sender(self):
        """Restart WebSocket sender"""
        logger.info("Restarting WebSocket sender...")
        self.stop_sender()
        time.sleep(2)  # Brief pause between stop and start
        return self.start_sender()

# Global instance
websocket_manager = WebSocketManager()