// frontend/src/hooks/useWebSocket.ts
import { useEffect, useState, useRef, useCallback } from 'react';

type WebSocketStatus = 'connecting' | 'open' | 'closed' | 'error';

interface UseWebSocketOptions {
  url: string; // Should be the base URL, e.g., ws://localhost:8000/ws/{user_id}
  onMessage?: (event: MessageEvent) => void;
  onError?: (event: Event) => void;
  onOpen?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
  reconnectLimit?: number;
  reconnectInterval?: number;
  // Placeholder for authentication - actual implementation will vary
  getAuthToken?: () => string | null;
  getUserId?: () => string | null; // Function to get user ID
}

interface UseWebSocketReturn {
  sendMessage: (data: any) => void;
  connectionStatus: WebSocketStatus;
  lastMessage: MessageEvent | null;
  wsInstance: WebSocket | null;
}

const useWebSocket = ({
  url,
  onMessage,
  onError,
  onOpen,
  onClose,
  reconnectLimit = 0, // 0 means no reconnection attempts
  reconnectInterval = 5000, // 5 seconds
  getAuthToken,
  getUserId,
}: UseWebSocketOptions): UseWebSocketReturn => {
  const [connectionStatus, setConnectionStatus] = useState<WebSocketStatus>('closed');
  const [lastMessage, setLastMessage] = useState<MessageEvent | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log('WebSocket already open.');
      return;
    }

    setConnectionStatus('connecting');
    
    // Ensure currentUserId is always a string for the replace method
    const userIdFromFunc = getUserId ? getUserId() : null;
    const currentUserId = userIdFromFunc !== null ? userIdFromFunc : 'default_user'; // Replace with actual user ID logic
    const currentToken = getAuthToken ? getAuthToken() : null; // Replace with actual token logic
    
    let finalUrl = url.replace('{user_id}', currentUserId);
    if (currentToken) {
      // Ensure token is appended correctly, handling existing query params if any (though {user_id} likely won't have them)
      finalUrl += `${finalUrl.includes('?') ? '&' : '?'}token=${currentToken}`; 
    }

    console.log(`Attempting to connect to WebSocket: ${finalUrl}`);
    try {
      const ws = new WebSocket(finalUrl);
      wsRef.current = ws;

      ws.onopen = (event) => {
        console.log('WebSocket connection established.');
        setConnectionStatus('open');
        reconnectAttemptsRef.current = 0; 
        if (onOpen) {
          onOpen(event);
        }
        // Example: Send authentication message if required by backend after connection
        // if (currentToken && some_condition_for_post_auth_message) {
        //   ws.send(JSON.stringify({ type: 'auth', payload: { token: currentToken } }));
        // }
      };

      ws.onmessage = (event) => {
        console.log('WebSocket message received:', event.data);
        setLastMessage(event);
        if (onMessage) {
          onMessage(event);
        }
      };

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setConnectionStatus('error');
        if (onError) {
          onError(event);
        }
        // Optionally attempt reconnect on error too, depending on strategy
        // ws.close(); // Ensure it's closed before trying to reconnect from onclose
      };

      ws.onclose = (event) => {
        console.log(`WebSocket connection closed. Code: ${event.code}, Reason: ${event.reason}, Was Clean: ${event.wasClean}`);
        setConnectionStatus('closed');
        wsRef.current = null; // Clear the ref
        if (onClose) {
          onClose(event);
        }

        if (reconnectLimit > 0 && reconnectAttemptsRef.current < reconnectLimit) {
          reconnectAttemptsRef.current++;
          console.log(`Attempting to reconnect (${reconnectAttemptsRef.current}/${reconnectLimit})...`);
          setTimeout(connect, reconnectInterval);
        } else if (reconnectLimit > 0 && reconnectAttemptsRef.current >= reconnectLimit) {
          console.error('WebSocket reconnect limit reached.');
        }
      };
    } catch (err) {
        console.error("Failed to create WebSocket:", err);
        setConnectionStatus('error');
        // Potentially try to reconnect here too if appropriate for the error type
    }
  }, [url, onOpen, onMessage, onError, onClose, reconnectLimit, reconnectInterval, getAuthToken, getUserId]);

  useEffect(() => {
    if (url && connectionStatus === 'closed' && reconnectAttemptsRef.current === 0) {
        connect();
    }
    
    return () => {
      if (wsRef.current) {
        console.log('Closing WebSocket connection on cleanup.');
        wsRef.current.onopen = null;
        wsRef.current.onmessage = null;
        wsRef.current.onerror = null;
        wsRef.current.onclose = null; // Prevent onclose from triggering reconnects during cleanup
        wsRef.current.close();
        wsRef.current = null;
      }
      reconnectAttemptsRef.current = 0; // Reset for next mount if needed
    };
  }, [url, connect, connectionStatus]); // connect is a dependency

  const sendMessage = useCallback((data: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        const message = typeof data === 'string' ? data : JSON.stringify(data);
        wsRef.current.send(message);
        console.log('WebSocket message sent:', data);
      } catch (error) {
        console.error('Failed to send WebSocket message:', error);
      }
    } else {
      console.warn('WebSocket connection is not open. Message not sent:', data);
    }
  }, []);

  return { sendMessage, connectionStatus, lastMessage, wsInstance: wsRef.current };
};

export default useWebSocket;