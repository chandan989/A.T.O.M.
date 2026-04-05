import { useState, useMemo, useEffect, useCallback } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import Metric from '../components/Metric';
import Button from '../components/Button';
import MoleculeViewer from '../components/MoleculeViewer';
import ConnectionDialog from '../components/ConnectionDialog';
import { useAtomConnection } from '../lib/atomClient';
import { useAtomSession, SessionStep } from '../hooks/useAtomSession';
import { rewardComponents } from '../data/mockChartData';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip, ReferenceLine } from 'recharts';

const Playground = () => {
  const { isConnected, status: connStatus } = useAtomConnection();
  const session = useAtomSession();
  const [selectedTask, setSelectedTask] = useState<number>(1);
  const [showConnectionDialog, setShowConnectionDialog] = useState(false);

  // Load tasks when connected
  useEffect(() => {
    if (isConnected) {
      session.loadTasks();
    }
  }, [isConnected]);

  const handleStartSession = async () => {
    await session.reset(selectedTask);
  };

  const handleReset = async () => {
    await session.reset(selectedTask);
  };

  // Derive chart data from session steps
  const chartData = useMemo(() =>
    session.steps.map(s => ({
      step: s.step,
      QED: s.properties.QED ?? 0,
      LogP: s.properties.LogP ?? 0,
    })),
    [session.steps]
  );

  // Build console log from step messages
  const consoleLog = useMemo(() =>
    session.steps.map(s => s.message).join('\n\n'),
    [session.steps]
  );

  // Current step data
  const currentStep = session.steps.length > 0 ? session.steps[session.steps.length - 1] : null;
  const isFinished = currentStep?.done ?? false;

  // Check if current properties are in target
  const isInTarget = useCallback((step: SessionStep | null): boolean => {
    if (!step || !step.targetProfile) return false;
    return Object.entries(step.targetProfile).every(([key, [min, max]]) => {
      const val = step.properties[key];
      return val !== undefined && val >= min && val <= max;
    });
  }, []);

  // Score breakdown (computed from current state)
  const scoreBreakdown = useMemo(() => {
    if (!currentStep) {
      return rewardComponents.map(r => ({
        component: r.name.split(' ')[0],
        value: 0,
        weight: r.weight,
        color: r.color,
      }));
    }
    const inTarget = isInTarget(currentStep);
    const stepCount = session.steps.length;
    return [
      { component: 'Target', value: inTarget ? 0.95 : 0.3, weight: 40, color: '#7B3EFC' },
      { component: 'Trajectory', value: Math.min(1, stepCount * 0.2), weight: 25, color: '#CCFF00' },
      { component: 'Efficiency', value: isFinished ? 0.9 : 0.5, weight: 15, color: '#FF5415' },
      { component: 'Validity', value: 1.0, weight: 10, color: '#FFFFFF' },
      { component: 'Diversity', value: Math.min(1, stepCount * 0.25), weight: 10, color: '#E5E5E5' },
    ];
  }, [currentStep, isFinished, session.steps.length, isInTarget]);

  // ── NOT CONNECTED STATE ───────────────────────────────────
  if (!isConnected) {
    return (
      <main>
        <Navbar />
        <section className="section bg-chem-dark">
          <div className="page-header">
            <h1 className="page-header-title">PLAYGROUND</h1>
            <p className="page-header-subtitle">
              Connect to an ATOM server to start an interactive session
            </p>
          </div>
        </section>

        <section className="section bg-chem-light">
          <div className="playground-not-connected">
            <div className="playground-not-connected-icon">⚡</div>
            <h2 className="playground-not-connected-title">SERVER NOT CONNECTED</h2>
            <p className="playground-not-connected-desc">
              Click INITIALIZE in the navigation bar to connect to your ATOM server deployed on HuggingFace Spaces.
            </p>
            <Button variant="primary" onClick={() => setShowConnectionDialog(true)}>
              CONNECT TO SERVER
            </Button>
          </div>
        </section>

        <Footer />
        <ConnectionDialog isOpen={showConnectionDialog} onClose={() => setShowConnectionDialog(false)} />
      </main>
    );
  }

  // ── CONNECTED STATE ─────────────────────────────────────────
  return (
    <main>
      <Navbar />

      <section className="section bg-chem-dark">
        <div className="page-header">
          <h1 className="page-header-title">PLAYGROUND</h1>
          <p className="page-header-subtitle">
            Live interactive environment — watch the AI optimize molecules in real-time
          </p>
        </div>
      </section>

      <section className="section bg-chem-light">
        {/* Session Controls Bar */}
        <div className="session-controls">
          <div className="session-controls-left">
            <label className="session-label">TASK</label>
            <select
              className="session-select"
              value={selectedTask}
              onChange={e => setSelectedTask(Number(e.target.value))}
            >
              {session.tasks.length > 0 ? (
                session.tasks.map(t => (
                  <option key={t.task_id} value={t.task_id}>
                    Task {t.task_id} — {t.difficulty} (max {t.max_steps} steps)
                  </option>
                ))
              ) : (
                <>
                  <option value={1}>Task 1 — Easy</option>
                  <option value={2}>Task 2 — Medium</option>
                  <option value={3}>Task 3 — Hard</option>
                  <option value={4}>Task 4 — Extreme</option>
                </>
              )}
            </select>
          </div>
          <div className="session-controls-right">
            <button
              className="btn btn-primary"
              onClick={handleStartSession}
              disabled={session.status === 'resetting' || session.status === 'connecting_ws'}
            >
              {session.status === 'idle' || session.status === 'connecting_ws' ? 'START SESSION' : 'NEW SESSION'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleReset}
              disabled={session.status === 'idle' || session.status === 'resetting'}
            >
              RESET
            </button>
          </div>
        </div>

        {/* Error banner */}
        {session.error && (
          <div className="connection-banner connection-banner-error" style={{ margin: '0 var(--space-4)' }}>
            ✗ {session.error}
          </div>
        )}

        <div className="playground-layout">
          {/* LEFT — MOLECULE STATE */}
          <div className="playground-panel">
            <div className="playground-panel-title">MOLECULE STATE</div>

            {/* Molecule Visualization */}
            <MoleculeViewer
              smiles={currentStep?.smiles || ''}
              width={280}
              height={200}
              label="CURRENT MOLECULE"
            />

            {/* SMILES display */}
            <div className="playground-smiles" style={{ marginTop: 'var(--space-3)' }}>
              {currentStep?.smiles || '—'}
            </div>

            {/* Properties grid */}
            <div className="playground-props-grid">
              <Metric
                value={(currentStep?.properties?.QED ?? 0).toFixed(2)}
                label="QED"
                color={currentStep && isInTarget(currentStep) ? '#CCFF00' : undefined}
              />
              <Metric
                value={(currentStep?.properties?.LogP ?? 0).toFixed(2)}
                label="LogP"
                color={currentStep && isInTarget(currentStep) ? '#CCFF00' : undefined}
              />
              <Metric
                value={(currentStep?.properties?.SA_Score ?? 0).toFixed(1)}
                label="SA_SCORE"
              />
              <Metric
                value={(currentStep?.properties?.MW ?? 0).toFixed(0)}
                label="MW"
              />
            </div>

            {/* Target Profile */}
            {currentStep && currentStep.targetProfile && (
              <div style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--text-mono)',
                textTransform: 'uppercase',
                color: '#666',
                marginTop: 'var(--space-3)',
              }}>
                TARGET PROFILE:
                {Object.entries(currentStep.targetProfile).map(([key, [min, max]]) => (
                  <div key={key} style={{ marginLeft: 'var(--space-2)' }}>
                    {key}: [{min}, {max}]
                  </div>
                ))}
              </div>
            )}

            {/* In-target indicator */}
            {currentStep && (
              <div style={{
                marginTop: 'var(--space-2)',
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--text-mono)',
                color: isInTarget(currentStep) ? '#CCFF00' : '#FF5415',
                fontWeight: 700,
                backgroundColor: '#000',
                padding: 'var(--space-2) var(--space-3)',
              }}>
                {isInTarget(currentStep) ? '✓ IN TARGET' : '✗ OUTSIDE TARGET'}
              </div>
            )}
          </div>

          {/* CENTER — AGENT CONSOLE */}
          <div className="playground-panel">
            <div className="playground-panel-title">AGENT CONSOLE</div>
            <div className="playground-console">
              {session.status === 'idle' || session.status === 'connecting_ws' ? (
                <span style={{ color: '#666' }}>
                  {'> Waiting for session start...\n> Select a task and click START SESSION'}
                  {session.wsConnected && '\n> ● WebSocket connected — live updates enabled'}
                </span>
              ) : (
                consoleLog || '> Environment ready.'
              )}
            </div>

            {/* Session Status */}
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 'var(--text-mono)',
              textTransform: 'uppercase',
              padding: 'var(--space-2) var(--space-3)',
              backgroundColor: session.status === 'running' ? '#000' : session.status === 'finished' ? '#000' : 'transparent',
              color: session.status === 'running' ? '#CCFF00' : session.status === 'finished' ? '#7B3EFC' : '#666',
              border: session.status !== 'idle' && session.status !== 'connecting_ws' ? '1px solid #333' : 'none',
              marginBottom: 'var(--space-3)',
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-2)',
            }}>
              {session.status === 'running' && (
                <span className="navbar-status-dot" />
              )}
              STATUS: {session.status.toUpperCase()}
              {session.wsConnected && (
                <span style={{ marginLeft: 'auto', color: '#CCFF00', fontSize: '10px' }}>● WS LIVE</span>
              )}
            </div>
          </div>

          {/* RIGHT — TRAJECTORY */}
          <div className="playground-panel">
            <div className="playground-panel-title">TRAJECTORY</div>
            <div className="playground-step-counter">
              STEP {currentStep?.step ?? 0} / {currentStep ? (session.tasks.find(t => t.task_id === selectedTask)?.max_steps ?? '?') : '—'}
            </div>

            {/* Trajectory chart */}
            {session.steps.length > 0 && (
              <div style={{ marginBottom: 'var(--space-4)' }}>
                <ResponsiveContainer width="100%" height={180}>
                  <LineChart data={chartData}>
                    <XAxis dataKey="step" stroke="#666" tick={{ fontFamily: 'Fira Code', fontSize: 12 }} />
                    <YAxis stroke="#666" tick={{ fontFamily: 'Fira Code', fontSize: 12 }} domain={[0, 'auto']} />
                    <Line type="monotone" dataKey="QED" stroke="#7B3EFC" strokeWidth={2} dot={{ fill: '#7B3EFC', r: 4 }} />
                    <Line type="monotone" dataKey="LogP" stroke="#CCFF00" strokeWidth={2} dot={{ fill: '#CCFF00', r: 4 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#000',
                        border: '2px solid #1A1A1A',
                        fontFamily: 'Fira Code, monospace',
                        fontSize: '12px',
                        color: '#FFF',
                        borderRadius: 0,
                      }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Score Breakdown */}
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              textTransform: 'uppercase',
              color: '#666',
              marginBottom: 'var(--space-2)',
              fontWeight: 700,
            }}>
              SCORE BREAKDOWN
            </div>
            {scoreBreakdown.map(s => (
              <div className="progress-bar" key={s.component}>
                <span className="progress-bar-label">{s.component}</span>
                <div className="progress-bar-track">
                  <div
                    className="progress-bar-fill"
                    style={{
                      width: `${s.value * 100}%`,
                      backgroundColor: s.color,
                    }}
                  />
                </div>
                <span className="progress-bar-value">{(s.value * s.weight / 100).toFixed(2)}</span>
              </div>
            ))}

            {/* Final Score */}
            {isFinished && currentStep && (
              <div className="playground-score" style={{ marginTop: 'var(--space-4)' }}>
                {currentStep.reward.toFixed(2)}
              </div>
            )}
          </div>
        </div>
      </section>

      <Footer />
    </main>
  );
};

export default Playground;
