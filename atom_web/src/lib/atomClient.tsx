/**
 * A.T.O.M. Server API Client
 *
 * Central module for communicating with the ATOM backend.
 * Handles connection config, auth, and all API calls.
 */

import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';

// ── Types ──────────────────────────────────────────────────────

export interface ConnectionConfig {
  serverUrl: string;
  apiKey: string;
}

export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

export interface TaskDefinition {
  task_id: number;
  difficulty: string;
  starting_scaffold: string;
  max_steps: number;
  tpp: Record<string, [number, number]>;
}

export interface AtomObservation {
  current_smiles: string;
  current_properties: Record<string, number>;
  target_profile: Record<string, [number, number]>;
  message: string;
  valid_sites: any[] | null;
  step_number: number;
  max_steps: number;
  done: boolean;
  trajectory_summary: Record<string, any>;
  reward: number;
}

export interface AtomConnectionContextType {
  config: ConnectionConfig | null;
  status: ConnectionStatus;
  error: string | null;
  connect: (url: string, apiKey: string) => Promise<boolean>;
  disconnect: () => void;
  isConnected: boolean;
}

// ── localStorage helpers ───────────────────────────────────────

const STORAGE_KEY = 'atom_connection';

export function loadConnectionConfig(): ConnectionConfig | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function saveConnectionConfig(config: ConnectionConfig): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
}

export function clearConnectionConfig(): void {
  localStorage.removeItem(STORAGE_KEY);
}

// ── API helpers ────────────────────────────────────────────────

function normalizeUrl(url: string): string {
  return url.replace(/\/+$/, '');
}

async function apiFetch(config: ConnectionConfig, path: string, options: RequestInit = {}): Promise<Response> {
  const url = `${normalizeUrl(config.serverUrl)}${path}`;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${config.apiKey}`,
    ...(options.headers as Record<string, string> || {}),
  };
  return fetch(url, { ...options, headers });
}

export async function verifyConnection(serverUrl: string, apiKey: string): Promise<{ ok: boolean; message: string }> {
  try {
    const config = { serverUrl: normalizeUrl(serverUrl), apiKey };
    const resp = await apiFetch(config, '/auth/verify');
    if (resp.ok) {
      const data = await resp.json();
      return { ok: true, message: data.message || 'Connected' };
    }
    const err = await resp.json().catch(() => ({ detail: 'Connection failed' }));
    return { ok: false, message: err.detail || `HTTP ${resp.status}` };
  } catch (e: any) {
    return { ok: false, message: e.message || 'Network error' };
  }
}

export async function fetchTasks(config: ConnectionConfig): Promise<TaskDefinition[]> {
  const resp = await apiFetch(config, '/tasks');
  if (!resp.ok) throw new Error(`Failed to fetch tasks: ${resp.status}`);
  const data = await resp.json();
  return data.tasks;
}

export async function resetEnvironment(config: ConnectionConfig, taskId: number): Promise<AtomObservation> {
  const resp = await apiFetch(config, `/env/reset?task_id=${taskId}`, { method: 'POST' });
  if (!resp.ok) throw new Error(`Reset failed: ${resp.status}`);
  const data = await resp.json();
  return data.observation;
}

export async function getEnvironmentState(config: ConnectionConfig): Promise<any> {
  const resp = await apiFetch(config, '/env/state');
  if (!resp.ok) throw new Error(`State fetch failed: ${resp.status}`);
  return resp.json();
}

export async function stepEnvironment(config: ConnectionConfig, action: Record<string, any>): Promise<{ observation: AtomObservation; reward: number }> {
  const resp = await apiFetch(config, '/env/step', {
    method: 'POST',
    body: JSON.stringify(action),
  });
  if (!resp.ok) throw new Error(`Step failed: ${resp.status}`);
  return resp.json();
}

// ── React Context ──────────────────────────────────────────────

const AtomConnectionContext = createContext<AtomConnectionContextType | null>(null);

export function AtomConnectionProvider({ children }: { children: ReactNode }) {
  const [config, setConfig] = useState<ConnectionConfig | null>(loadConnectionConfig);
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [error, setError] = useState<string | null>(null);

  // Auto-verify on mount if config exists
  useEffect(() => {
    if (config) {
      setStatus('connecting');
      verifyConnection(config.serverUrl, config.apiKey).then(result => {
        if (result.ok) {
          setStatus('connected');
          setError(null);
        } else {
          setStatus('error');
          setError(result.message);
        }
      });
    }
  }, []);

  const connect = useCallback(async (url: string, apiKey: string): Promise<boolean> => {
    setStatus('connecting');
    setError(null);

    const result = await verifyConnection(url, apiKey);
    if (result.ok) {
      const newConfig = { serverUrl: normalizeUrl(url), apiKey };
      setConfig(newConfig);
      saveConnectionConfig(newConfig);
      setStatus('connected');
      return true;
    } else {
      setStatus('error');
      setError(result.message);
      return false;
    }
  }, []);

  const disconnect = useCallback(() => {
    setConfig(null);
    setStatus('disconnected');
    setError(null);
    clearConnectionConfig();
  }, []);

  return (
    <AtomConnectionContext.Provider value={{
      config,
      status,
      error,
      connect,
      disconnect,
      isConnected: status === 'connected',
    }}>
      {children}
    </AtomConnectionContext.Provider>
  );
}

export function useAtomConnection(): AtomConnectionContextType {
  const ctx = useContext(AtomConnectionContext);
  if (!ctx) throw new Error('useAtomConnection must be used within AtomConnectionProvider');
  return ctx;
}
