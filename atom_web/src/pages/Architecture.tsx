import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import SectionHeader from '../components/SectionHeader';
import DataTable from '../components/DataTable';
import Tag from '../components/Tag';
import { Brain, Shield, Server, ArrowRightLeft, Database, TerminalSquare } from 'lucide-react';
import { architectureComponents, apiEndpoints, dataFlowSteps } from '../data/mockArchitecture';

const Architecture = () => (
  <main>
    <Navbar />

    <section className="section bg-chem-dark">
      <div className="page-header">
        <h1 className="page-header-title">SYSTEM ARCHITECTURE</h1>
        <p className="page-header-subtitle">
          OpenEnv client-server architecture with Dual-Agent inference
        </p>
      </div>
    </section>

    {/* ARCHITECTURE DIAGRAM */}
    <section className="section bg-chem-light">
      <div className="content-section">
        <SectionHeader title="ARCHITECTURE OVERVIEW" subtitle="Interactive high-level dual agent workflow" />
        <div className="three-col" style={{ marginTop: 'var(--space-5)' }}>
          
          {/* Environment Side */}
          <div className="feature-card" style={{ backgroundColor: 'var(--color-white)', padding: 0 }}>
            <div className="arch-box-header" style={{ backgroundColor: 'var(--color-purple)', color: '#FFF', padding: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <Server size={24} />
              <span style={{ fontSize: '18px' }}>ATOM ENVIRONMENT</span>
            </div>
            <div className="arch-box-body" style={{ padding: 'var(--space-4)', display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
              {architectureComponents.filter(c => c.type !== 'agent').map((c, i) => (
                <div className="arch-block" key={c.id} style={{ 
                  backgroundColor: 'var(--color-black)', 
                  color: 'var(--color-green)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-3)'
                }}>
                  {i === 0 ? <TerminalSquare size={20} /> : <Database size={20} />}
                  <span>{c.label}</span>
                </div>
              ))}
            </div>
          </div>
          
          {/* Connection Side */}
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: 'var(--space-4)', borderBottom: 'var(--border-medium) solid var(--color-black)' }}>
            <div style={{ 
              color: 'var(--color-green)', 
              backgroundColor: '#000',
              padding: 'var(--space-3)',
              border: '4px solid var(--color-purple)',
              boxShadow: '4px 4px 0px 0px var(--color-purple)'
            }}>
              <ArrowRightLeft size={48} strokeWidth={3} />
            </div>
            <div style={{ fontSize: '18px', fontFamily: 'var(--font-mono)', fontWeight: 'bold', marginTop: 'var(--space-4)' }}>
              HTTP / WS
            </div>
          </div>

          {/* Dual Agent Side */}
          <div className="feature-card" style={{ backgroundColor: 'var(--color-white)', padding: 0 }}>
             <div className="arch-box-header" style={{ backgroundColor: 'var(--color-black)', color: 'var(--color-green)', padding: 'var(--space-4)', display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
              <Brain size={24} />
              <span style={{ fontSize: '18px' }}>ACTOR-CRITIC LOOP</span>
            </div>
            <div className="arch-box-body" style={{ padding: 'var(--space-4)', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              <div className="arch-block" style={{ borderColor: 'var(--color-green)', backgroundColor: '#FAFAFA' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-1)' }}>
                   <Brain size={20} color="var(--color-green)" style={{ fill: 'var(--color-black)' }} />
                   <div style={{ fontFamily: 'var(--font-sans)', fontWeight: 800, fontSize: '18px' }}>GENERATOR</div>
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>Proposes Molecules</div>
              </div>
              <div className="arch-block" style={{ borderColor: 'var(--color-orange)', backgroundColor: '#FAFAFA' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', marginBottom: 'var(--space-1)' }}>
                   <Shield size={20} color="var(--color-orange)" style={{ fill: 'var(--color-black)' }} />
                   <div style={{ fontFamily: 'var(--font-sans)', fontWeight: 800, fontSize: '18px' }}>CRITIC</div>
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>Validates & Filters</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    {/* DATA FLOW */}
    <section className="section bg-chem-dark" style={{ color: '#FFFFFF' }}>
      <div className="content-section">
        <SectionHeader title="DATA FLOW" dark subtitle="Synchronous environment simulation steps" />
        <div className="timeline" style={{ marginTop: 'var(--space-5)' }}>
          {dataFlowSteps.map((step, index) => (
            <div className="timeline-item" key={step.step} style={{ 
              backgroundColor: '#1A1A1A',
              padding: 'var(--space-4)',
              borderBottom: '1px solid #333'
            }}>
              <div className="timeline-number" style={{ fontSize: '32px', color: 'var(--color-purple)' }}>0{step.step}</div>
              <div className="timeline-text" style={{ color: '#FFF' }}>{step.description}</div>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* DUAL AGENT DETAIL */}
    <section className="section bg-chem-light">
      <div className="content-section">
        <SectionHeader title="DUAL-AGENT DETAIL" subtitle="In-depth breakdown of the actor-critic implementation" />
        <div className="two-col" style={{ marginTop: 'var(--space-5)' }}>
          <div style={{ padding: '0' }}>
            <div className="task-card" style={{ height: '100%', borderColor: 'var(--color-black)' }}>
              <div className="task-card-header" style={{ backgroundColor: 'var(--color-black)', color: 'var(--color-green)', borderBottomColor: 'var(--color-black)' }}>
                <Brain size={32} />
                <h3 style={{ margin: 0, fontFamily: 'var(--font-sans)', fontWeight: 800, fontSize: '24px' }}>GENERATOR</h3>
              </div>
              <div className="task-card-body" style={{ backgroundColor: '#FFF' }}>
                <p style={{ fontFamily: 'var(--font-mono)', fontSize: '16px', lineHeight: 1.6, color: '#333' }}>
                  Proposes fragments & sites based on current molecular state. Uses spatial reasoning to select optimal modification points.
                </p>
                <div style={{ marginTop: 'auto', paddingTop: 'var(--space-3)' }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: '#666', textTransform: 'uppercase' }}>Model Type</div>
                  <div style={{ fontFamily: 'var(--font-display)', fontSize: '24px', color: 'var(--color-purple)' }}>LLM / Actor</div>
                </div>
              </div>
            </div>
          </div>
          <div style={{ padding: '0' }}>
            <div className="task-card" style={{ height: '100%', borderColor: 'var(--color-black)' }}>
              <div className="task-card-header" style={{ backgroundColor: 'var(--color-black)', color: 'var(--color-orange)', borderBottomColor: 'var(--color-black)' }}>
                <Shield size={32} />
                <h3 style={{ margin: 0, fontFamily: 'var(--font-sans)', fontWeight: 800, fontSize: '24px' }}>CRITIC</h3>
              </div>
              <div className="task-card-body" style={{ backgroundColor: '#FFF' }}>
                <p style={{ fontFamily: 'var(--font-mono)', fontSize: '16px', lineHeight: 1.6, color: '#333' }}>
                  Validates proposals against chemical heuristics. Checks Lipinski rules, PAINS filters. Approves or rejects with reasoning.
                </p>
                <div style={{ marginTop: 'auto', paddingTop: 'var(--space-3)' }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: '#666', textTransform: 'uppercase' }}>Model Type</div>
                  <div style={{ fontFamily: 'var(--font-display)', fontSize: '24px', color: 'var(--color-purple)' }}>Rules / Critic</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    {/* API ENDPOINTS */}
    <section className="section bg-chem-dark" style={{ color: '#FFFFFF' }}>
      <div className="content-section">
        <SectionHeader title="API ENDPOINTS" dark />
        <DataTable
          dark
          headers={['Method', 'Path', 'Description', 'Response']}
          rows={apiEndpoints.map(e => [
            <Tag key={e.method + e.path} color={e.method === 'POST' ? 'purple' : e.method === 'WS' ? 'orange' : 'green'}>{e.method}</Tag>,
            e.path,
            e.description,
            e.response || '—',
          ])}
        />
      </div>
    </section>

    <Footer />
  </main>
);

export default Architecture;
