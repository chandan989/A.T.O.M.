/**
 * useAtomSession — React hook for managing a live ATOM session.
 *
 * Connects via WebSocket to the ATOM server's /ws/observe endpoint
 * to receive real-time trajectory updates as the AI agent runs.
 * Also supports resetting the environment via REST.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import {
  useAtomConnection,
  resetEnvironment,
  fetchTasks,
  AtomObservation,
  TaskDefinition,
} from '../lib/atomClient';

export interface SessionStep {
  step: number;
  smiles: string;
  properties: Record<string, number>;
  message: string;
  done: boolean;
  reward: number;
  targetProfile: Record<string, [number, number]>;
}

export type SessionStatus = 'idle' | 'connecting_ws' | 'resetting' | 'running' | 'finished' | 'error';

export interface AtomSession {
  status: SessionStatus;
  steps: SessionStep[];
  currentObservation: AtomObservation | null;
  tasks: TaskDefinition[];
  error: string | null;
  wsConnected: boolean;
  reset: (taskId: number) => Promise<void>;
  loadTasks: () => Promise<void>;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}

function observationToStep(obs: AtomObservation, reward?: number): SessionStep {
  return {
    step: obs.step_number,
    smiles: obs.current_smiles,
    properties: obs.current_properties,
    message: obs.message,
    done: obs.done,
    reward: reward ?? obs.reward ?? 0,
    targetProfile: obs.target_profile,
  };
}

export function useAtomSession(): AtomSession {
  const { config, isConnected } = useAtomConnection();
  const [status, setStatus] = useState<SessionStatus>('idle');
  const [steps, setSteps] = useState<SessionStep[]>([]);
  const [currentObservation, setCurrentObservation] = useState<AtomObservation | null>(null);
  const [tasks, setTasks] = useState<TaskDefinition[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const loadTasks = useCallback(async () => {
    if (!config || !isConnected) return;
    try {
      const taskList = await fetchTasks(config);
      setTasks(taskList);
    } catch (e: any) {
      setError(e.message);
    }
  }, [config, isConnected]);

  // Process incoming WebSocket messages
  const handleWsMessage = useCallback((event: MessageEvent) => {
    try {
      const msg = JSON.parse(event.data);

      if (msg.type === 'connected') {
        console.log('[WS] Connected:', msg.message);
        return;
      }

      if (msg.type === 'pong') {
        return;
      }

      if (msg.type === 'reset') {
        const obs = msg.data?.observation as AtomObservation;
        if (obs) {
          setCurrentObservation(obs);
          const step = observationToStep(obs);
          setSteps([step]);
          setStatus('running');
          setError(null);
        }
        return;
      }

      if (msg.type === 'step') {
        const obs = msg.data?.observation as AtomObservation;
        const reward = msg.data?.reward ?? 0;
        if (obs) {
          setCurrentObservation(obs);
          const step = observationToStep(obs, reward);
          setSteps(prev => [...prev, step]);

          if (obs.done) {
            setStatus('finished');
          }
        }
        return;
      }
    } catch (e) {
      console.error('[WS] Failed to parse message:', e);
    }
  }, []);

  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    if (!config || !isConnected) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setStatus('connecting_ws');
    const serverUrl = config.serverUrl.replace(/\/+$/, '');
    const wsUrl = serverUrl
      .replace(/^https:/, 'wss:')
      .replace(/^http:/, 'ws:');
    const fullUrl = `${wsUrl}/ws/observe?token=${encodeURIComponent(config.apiKey)}`;

    console.log('[WS] Connecting to:', fullUrl);
    const ws = new WebSocket(fullUrl);

    ws.onopen = () => {
      console.log('[WS] Connected');
      setWsConnected(true);
      setStatus('idle');
      setError(null);
      reconnectAttemptsRef.current = 0;
    };

    ws.onmessage = handleWsMessage;

    ws.onerror = (e) => {
      console.error('[WS] Error:', e);
      setError('WebSocket connection error');
    };

    ws.onclose = (e) => {
      console.log('[WS] Closed:', e.code, e.reason);
      setWsConnected(false);
      wsRef.current = null;

      // Auto-reconnect with exponential backoff (max 5 attempts)
      if (reconnectAttemptsRef.current < 5 && e.code !== 4001) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 16000);
        reconnectAttemptsRef.current++;
        console.log(`[WS] Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current})`);
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, delay);
      } else if (e.code === 4001) {
        setError('WebSocket auth failed. Check your API key.');
        setStatus('error');
      }
    };

    wsRef.current = ws;
  }, [config, isConnected, handleWsMessage]);

  // Disconnect WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    reconnectAttemptsRef.current = 999; // Prevent auto-reconnect
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setWsConnected(false);
  }, []);

  // Reset environment via REST (triggers broadcast to WS observers)
  const reset = useCallback(async (taskId: number) => {
    if (!config || !isConnected) {
      setError('Not connected to server');
      return;
    }

    setStatus('resetting');
    setError(null);
    setSteps([]);

    try {
      const obs = await resetEnvironment(config, taskId);
      setCurrentObservation(obs);
      const step = observationToStep(obs);
      setSteps([step]);
      setStatus('running');
    } catch (e: any) {
      setError(e.message);
      setStatus('error');
    }
  }, [config, isConnected]);

  // Auto-connect WebSocket when server connection is established
  useEffect(() => {
    if (isConnected && config) {
      connectWebSocket();
    }
    return () => {
      disconnectWebSocket();
    };
  }, [isConnected, config]);

  // Ping to keep WebSocket alive every 30s
  useEffect(() => {
    if (!wsConnected) return;
    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ command: 'ping' }));
      }
    }, 30000);
    return () => clearInterval(interval);
  }, [wsConnected]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnectWebSocket();
    };
  }, [disconnectWebSocket]);

  return {
    status,
    steps,
    currentObservation,
    tasks,
    error,
    wsConnected,
    reset,
    loadTasks,
    connectWebSocket,
    disconnectWebSocket,
  };
}
