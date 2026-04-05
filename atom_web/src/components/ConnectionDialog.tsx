/**
 * ConnectionDialog — Auth popup for connecting to an ATOM server.
 *
 * Matches the brutalist design system with thick borders,
 * monospace fonts, and box shadows.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAtomConnection, verifyConnection } from '../lib/atomClient';
import { X } from 'lucide-react';

interface ConnectionDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

const ConnectionDialog = ({ isOpen, onClose }: ConnectionDialogProps) => {
  const { config, status, error: connectionError, connect, disconnect, isConnected } = useAtomConnection();
  const navigate = useNavigate();
  const [serverUrl, setServerUrl] = useState(config?.serverUrl || '');
  const [apiKey, setApiKey] = useState(config?.apiKey || '');
  const [testResult, setTestResult] = useState<{ ok: boolean; message: string } | null>(null);
  const [isTesting, setIsTesting] = useState(false);

  useEffect(() => {
    if (config) {
      setServerUrl(config.serverUrl);
      setApiKey(config.apiKey);
    }
  }, [config]);

  if (!isOpen) return null;

  const handleTest = async () => {
    if (!serverUrl || !apiKey) {
      setTestResult({ ok: false, message: 'Please fill in both fields' });
      return;
    }
    setIsTesting(true);
    setTestResult(null);
    const result = await verifyConnection(serverUrl, apiKey);
    setTestResult(result);
    setIsTesting(false);
  };

  const handleConnect = async () => {
    if (!serverUrl || !apiKey) return;
    const success = await connect(serverUrl, apiKey);
    if (success) {
      onClose();
      navigate('/playground');
    }
  };

  const handleDisconnect = () => {
    disconnect();
    setServerUrl('');
    setApiKey('');
    setTestResult(null);
  };

  const statusColor = isConnected ? '#CCFF00' : status === 'error' ? '#FF5415' : status === 'connecting' ? '#FFD700' : '#666';

  return (
    <div className="connection-overlay" onClick={onClose}>
      <div className="connection-dialog" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="connection-dialog-header">
          <div className="connection-dialog-title">
            <span className="connection-status-dot" style={{ backgroundColor: statusColor }} />
            {isConnected ? 'CONNECTED' : 'CONNECT TO ATOM SERVER'}
          </div>
          <button className="connection-dialog-close" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="connection-dialog-body">
          {/* Connection status banner */}
          {isConnected && (
            <div className="connection-banner connection-banner-success">
              ● CONNECTED TO {config?.serverUrl}
            </div>
          )}
          {status === 'error' && connectionError && (
            <div className="connection-banner connection-banner-error">
              ✗ {connectionError}
            </div>
          )}

          {/* Server URL Input */}
          <div className="connection-field">
            <label className="connection-label">HUGGINGFACE SPACE URL</label>
            <input
              type="url"
              className="connection-input"
              value={serverUrl}
              onChange={e => setServerUrl(e.target.value)}
              placeholder="https://username-atom.hf.space"
              spellCheck={false}
            />
          </div>

          {/* API Key Input */}
          <div className="connection-field">
            <label className="connection-label">API KEY</label>
            <input
              type="password"
              className="connection-input"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
              placeholder="Enter the API key from server console"
              spellCheck={false}
            />
          </div>

          {/* Test Result */}
          {testResult && (
            <div className={`connection-banner ${testResult.ok ? 'connection-banner-success' : 'connection-banner-error'}`}>
              {testResult.ok ? '✓' : '✗'} {testResult.message}
            </div>
          )}

          {/* Actions */}
          <div className="connection-actions">
            <button
              className="btn btn-secondary connection-action-btn"
              onClick={handleTest}
              disabled={isTesting || !serverUrl || !apiKey}
            >
              {isTesting ? 'TESTING...' : 'TEST CONNECTION'}
            </button>
            <button
              className="btn btn-primary connection-action-btn"
              onClick={handleConnect}
              disabled={status === 'connecting' || !serverUrl || !apiKey}
            >
              {status === 'connecting' ? 'CONNECTING...' : 'CONNECT'}
            </button>
          </div>

          {isConnected && (
            <button
              className="btn btn-secondary connection-action-btn"
              onClick={handleDisconnect}
              style={{ marginTop: '8px', width: '100%', justifyContent: 'center', borderColor: '#FF5415', color: '#FF5415' }}
            >
              DISCONNECT
            </button>
          )}

          {/* Help text */}
          <div className="connection-help">
            <p>1. Deploy the ATOM server on HuggingFace Spaces</p>
            <p>2. Copy the API key printed in the server console</p>
            <p>3. Enter the Space URL and API key above</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConnectionDialog;
