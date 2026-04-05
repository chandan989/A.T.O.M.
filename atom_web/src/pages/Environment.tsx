import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import SectionHeader from '../components/SectionHeader';
import DataTable from '../components/DataTable';
import Tag from '../components/Tag';
import { Terminal, Dna, Layers, Crosshair, Microscope } from 'lucide-react';
import { fragments } from '../data/mockFragments';

const Environment = () => (
  <main>
    <Navbar />

    {/* PAGE HEADER */}
    <section className="section bg-chem-dark">
      <div className="page-header">
        <h1 className="page-header-title">WHAT IS ATOM?</h1>
        <p className="page-header-subtitle">
          A real-world OpenEnv reinforcement learning environment that simulates the drug lead optimization workflow.
        </p>
      </div>
    </section>

    {/* THE PROBLEM */}
    <section className="section bg-chem-light">
      <div className="two-col">
        <div className="content-section">
          <h3>THE DRUG DISCOVERY BOTTLENECK</h3>
          <p>The average cost to bring a drug to market: <strong>$2.6 billion.</strong> The timeline: <strong>10–15 years.</strong> The attrition rate: <strong>&gt;90%.</strong></p>
          <p>Lead optimization — the iterative process of modifying a chemical scaffold to achieve a target property profile — is where most drug candidates fail. Medicinal chemists manually propose, synthesize, and test hundreds of molecular variants.</p>
          <p>ATOM automates this reasoning loop with reinforcement learning agents that learn to navigate chemical space efficiently.</p>
        </div>
        <div className="content-section">
          <h3>DRUG DISCOVERY PIPELINE</h3>
          <div className="pipeline" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-3)', position: 'relative' }}>
            <div className="pipeline-step">[1] Ti TARGET ID</div>
            <div className="pipeline-step">[2] Hd HIT DISCOVERY</div>
            <div className="pipeline-step highlighted" style={{ backgroundColor: 'var(--color-black)', color: 'var(--color-green)' }}>[3] Lo ATOM LEAD OPTIMIZATION </div>
            <div className="pipeline-step">[4] Pc PRECLINICAL</div>
            <div className="pipeline-step">[5] Ct CLINICAL TRIALS</div>
            <div className="pipeline-step">[6] Fa FDA APPROVAL</div>
          </div>
        </div>
      </div>
    </section>

    {/* FLIGHT SIMULATOR ANALOGY */}
    <section className="section bg-chem-dark" style={{ color: '#FFFFFF' }}>
      <div className="content-section">
        <SectionHeader title="FLIGHT SIMULATOR ANALOGY" dark subtitle="How RL simulation translates to real-world drug discovery" />
        <div style={{ position: 'relative', marginTop: 'var(--space-5)', border: '4px solid #333', backgroundColor: '#0A0A0A', boxShadow: '8px 8px 0px 0px #000' }}>
          
          {/* Decorative Top Bar */}
          <div style={{ display: 'flex', borderBottom: '2px solid #333', padding: 'var(--space-2) var(--space-4)', backgroundColor: '#1A1A1A' }}>
            <div style={{ display: 'flex', gap: '8px' }}>
               <div style={{ width: '12px', height: '12px', backgroundColor: '#E63946', borderRadius: '50%' }}></div>
               <div style={{ width: '12px', height: '12px', backgroundColor: '#FFD166', borderRadius: '50%' }}></div>
               <div style={{ width: '12px', height: '12px', backgroundColor: '#06D6A0', borderRadius: '50%' }}></div>
            </div>
            <div style={{ flex: 1, textAlign: 'center', fontFamily: 'var(--font-mono)', fontSize: '12px', color: '#666' }}>SYS_MIGRATION_PROTOCOL</div>
          </div>

          <div className="two-col" style={{ position: 'relative' }}>
            <div style={{ padding: 'var(--space-6)', borderRight: '2px dashed #333', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <div style={{ fontSize: '64px', marginBottom: 'var(--space-4)', textAlign: 'center', color: '#FFF' }}><Terminal size={64} style={{ margin: '0 auto' }} /></div>
              <h3 style={{ fontFamily: 'var(--font-sans)', fontSize: 'var(--text-h2)', fontWeight: 700, textTransform: 'uppercase' as const, marginBottom: 'var(--space-3)', color: '#CCFF00', textAlign: 'center' }}>
                ATOM — THE FLIGHT SIMULATOR
              </h3>
              <div style={{ backgroundColor: '#1A1A1A', padding: 'var(--space-4)', border: '1px solid #333', fontFamily: 'var(--font-mono)', fontSize: '14px', lineHeight: 1.8, color: '#999' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>COMPUTE_ENV:</span> <span style={{ color: '#FFF' }}>RDKit Engine</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>ITERATION_SPEED:</span> <span style={{ color: '#FFF' }}>Milliseconds</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>DATA_SCALE:</span> <span style={{ color: '#FFF' }}>10^6 Episodes</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>RISK_FACTOR:</span> <span style={{ color: '#FFF' }}>Zero</span></div>
              </div>
            </div>
            
            {/* VS Badge */}
            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', backgroundColor: '#000', border: '4px solid #333', borderRadius: '50%', width: '80px', height: '80px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--font-display)', fontSize: '32px', color: '#FFF', zIndex: 10 }}>
              VS
            </div>

            <div style={{ padding: 'var(--space-6)', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <div style={{ fontSize: '64px', marginBottom: 'var(--space-4)', textAlign: 'center', color: '#FFF' }}><Dna size={64} style={{ margin: '0 auto' }} /></div>
              <h3 style={{ fontFamily: 'var(--font-sans)', fontSize: 'var(--text-h2)', fontWeight: 700, textTransform: 'uppercase' as const, marginBottom: 'var(--space-3)', color: '#FF5415', textAlign: 'center' }}>
                WET LAB REALITY
              </h3>
              <div style={{ backgroundColor: '#1A1A1A', padding: 'var(--space-4)', border: '1px solid #333', fontFamily: 'var(--font-mono)', fontSize: '14px', lineHeight: 1.8, color: '#999' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>COMPUTE_ENV:</span> <span style={{ color: '#FFF' }}>Physiological State</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>ITERATION_SPEED:</span> <span style={{ color: '#FFF' }}>Weeks/Months</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>DATA_SCALE:</span> <span style={{ color: '#FFF' }}>~10^2 Compounds</span></div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>RISK_FACTOR:</span> <span style={{ color: '#FFF' }}>Critical</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    {/* KEY INNOVATIONS */}
    <section className="section bg-chem-light">
      <div className="content-section">
        <SectionHeader title="KEY INNOVATIONS" />
      </div>
      <div className="three-col">
        <div className="feature-card" style={{ borderRight: 'var(--border-medium) solid #000', backgroundColor: '#FFF' }}>
          <div className="feature-card-badge">01</div>
          <div className="feature-card-content">
            <div style={{ marginBottom: 'var(--space-4)', color: 'var(--color-purple)' }}><Layers size={48} strokeWidth={1.5} /></div>
            <h3 className="feature-card-title">DUAL-MODE ACTION SPACE</h3>
            <p className="feature-card-desc">Mode 1: Scaffold & R-Group based modifications. Mode 2: Site enumeration with natural-language spatial descriptions bridging 2D graphs and 3D space.</p>
          </div>
        </div>
        <div className="feature-card" style={{ borderRight: 'var(--border-medium) solid #000', backgroundColor: '#FFF' }}>
          <div className="feature-card-badge">02</div>
          <div className="feature-card-content">
            <div style={{ marginBottom: 'var(--space-4)', color: 'var(--color-orange)' }}><Crosshair size={48} strokeWidth={1.5} /></div>
            <h3 className="feature-card-title">TRAJECTORY-AWARE REWARDS</h3>
            <p className="feature-card-desc">5-component scoring: Target Adherence (40%), Trajectory Quality (25%), Step Efficiency (15%), Chemical Validity (10%), Exploration Diversity (10%).</p>
          </div>
        </div>
        <div className="feature-card" style={{ backgroundColor: '#FFF' }}>
          <div className="feature-card-badge">03</div>
          <div className="feature-card-content">
            <div style={{ marginBottom: 'var(--space-4)', color: 'var(--color-green)' }}><Microscope size={48} strokeWidth={1.5} /></div>
            <h3 className="feature-card-title">REAL CHEMINFORMATICS</h3>
            <p className="feature-card-desc">RDKit-validated chemistry. Valency checks. PAINS filters. Lipinski Rule of 5. Real molecular graph operations ensuring synthetically viable proposals.</p>
          </div>
        </div>
      </div>
    </section>

    {/* ACTION SPACE TABLE */}
    <section className="section bg-chem-dark" style={{ color: '#FFFFFF' }}>
      <div className="content-section">
        <SectionHeader title="ACTION SPACE" dark />
        <DataTable
          dark
          headers={['Field', 'Type', 'Description']}
          rows={[
            ['action_type', 'string', '"add_fragment" | "get_valid_sites" | "finish"'],
            ['fragment_name', 'string?', 'Name of fragment to add (e.g., "methyl", "fluorine")'],
            ['site_id', 'int?', 'Target atom index for modification'],
            ['r_group', 'string?', 'R-group identifier for scaffold mode'],
          ]}
        />
      </div>
    </section>

    {/* OBSERVATION SPACE TABLE */}
    <section className="section bg-chem-light">
      <div className="content-section">
        <SectionHeader title="OBSERVATION SPACE" />
        <DataTable
          headers={['Field', 'Type', 'Description']}
          rows={[
            ['current_smiles', 'string', 'Current molecule in SMILES notation'],
            ['current_properties', 'dict', 'QED, LogP, SA_Score, MW, PAINS alerts'],
            ['target_profile', 'dict', 'Target property ranges to achieve'],
            ['message', 'string', 'Environment feedback message'],
            ['valid_sites', 'list', 'Available modification sites with descriptions'],
            ['step_number', 'int', 'Current step in episode'],
            ['max_steps', 'int', 'Maximum allowed steps'],
            ['done', 'bool', 'Whether episode has terminated'],
            ['trajectory_summary', 'dict', 'Running statistics of the optimization campaign'],
          ]}
        />
      </div>
    </section>

    {/* FRAGMENT LIBRARY */}
    <section className="section bg-chem-dark" style={{ color: '#FFFFFF' }}>
      <div className="content-section">
        <SectionHeader title="FRAGMENT LIBRARY" dark />
        <DataTable
          dark
          headers={['Category', 'Fragments', 'Pharmacological Role']}
          rows={fragments.map(f => [
            f.category,
            <span key={f.category} style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' as const }}>
              {f.fragments.map(frag => <Tag key={frag} color="green">{frag}</Tag>)}
            </span>,
            f.pharmacologicalRole,
          ])}
        />
      </div>
    </section>

    <Footer />
  </main>
);

export default Environment;
