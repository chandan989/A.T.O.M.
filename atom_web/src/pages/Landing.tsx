import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import MarqueeTape from '../components/MarqueeTape';
import TerminalInput from '../components/TerminalInput';
import TerminalWindow from '../components/TerminalWindow';
import DataBlock from '../components/DataBlock';
import FeatureCard from '../components/FeatureCard';
import StatsGrid from '../components/StatsGrid';
import Button from '../components/Button';
import Tag from '../components/Tag';
import Footer from '../components/Footer';
import { Grid3x3, Triangle, Shield, ArrowUpRight } from 'lucide-react';

const Landing = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress(p => {
        if (p >= 100) {
          clearInterval(timer);
          setTimeout(() => setIsLoading(false), 300);
          return 100;
        }
        return Math.min(100, p + Math.floor(Math.random() * 20) + 10);
      });
    }, 150);
    return () => clearInterval(timer);
  }, []);

  if (isLoading) {
    return (
      <div className="loading-screen bg-chem-light" style={{ position: 'fixed', inset: 0, display: 'flex', zIndex: 9999, color: 'var(--color-black)', backgroundColor: 'var(--color-white)', alignItems: 'stretch', justifyContent: 'stretch' }}>
        <div style={{ width: '100%', height: '100%', display: 'flex' }}>
          {/* LEFT SIDE: Content and Progress */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '10vw' }}>
            <div className="hero-version-badge" style={{ marginBottom: 'var(--space-4)', alignSelf: 'flex-start' }}>
              v2.0.4 // CORE UPDATE
            </div>
            <h1 className="hero-headline" style={{ marginBottom: 'var(--space-6)', color: 'var(--color-black)' }}>
              A.T.O.M.<br />INITIALIZING<br />ENVIRONMENT.
            </h1>
            
            {/* Terminal/Data-Block style progress */}
            <div className="data-block" style={{ width: '100%', maxWidth: '480px', backgroundColor: 'var(--color-white)', borderColor: 'var(--color-black)', boxShadow: 'var(--shadow-brutal)' }}>
              <div className="data-block-header" style={{ borderBottomColor: 'var(--color-black)', backgroundColor: 'var(--color-gray-light)' }}>
                <span className="data-block-live" style={{ color: 'var(--color-black)' }}>BOOT_SEQUENCE</span>
                <span className="data-block-id" style={{ color: 'var(--color-purple)' }}>{progress}%</span>
              </div>
              <div style={{ padding: 'var(--space-4)', display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: 'var(--text-mono)', fontWeight: 700, textTransform: 'uppercase', display: 'flex', justifyContent: 'space-between' }}>
                  <span>LOADING_MODULES</span>
                  <span>{progress < 100 ? 'IN PROGRESS' : 'COMPLETE'}</span>
                </div>
                <div className="loading-bar-container" style={{ borderColor: 'var(--color-black)', backgroundColor: 'var(--color-white)', height: '32px', padding: '4px' }}>
                  <div className="loading-bar" style={{ width: `${progress}%`, backgroundColor: 'var(--color-purple)', height: '100%', transition: 'width 0.15s ease-out' }}></div>
                </div>
                {/* Simulated log output based on progress */}
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: '#666', marginTop: 'var(--space-2)' }}>
                  {progress < 30 ? '> loading base dependencies...' : progress < 60 ? '> initializing molecular graphs...' : progress < 90 ? '> compiling RL environment...' : '> starting frontend...'}
                </div>
              </div>
            </div>
          </div>
          
          {/* RIGHT SIDE: Animated Logo */}
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', borderLeft: 'var(--border-medium) solid var(--color-black)', backgroundColor: 'var(--color-white)', position: 'relative', overflow: 'hidden' }}>
            {/* Grid background for the right side */}
            <div className="bg-grid-light" style={{ position: 'absolute', inset: 0, opacity: 0.5 }}></div>
            <img 
              src="/Logo.svg" 
              alt="A.T.O.M. Logo" 
              style={{ 
                height: '160px', 
                width: 'auto', 
                animation: 'pulse-dot 2s infinite',
                position: 'relative',
                zIndex: 2
              }} 
            />
          </div>
        </div>
      </div>
    );
  }

  return (
    <main>
      <Navbar />

      {/* HERO */}
      <section className="hero">
        <div className="hero-left bg-chem-light">
          <div className="hero-version-badge">v2.0.4 // CORE UPDATE</div>
          <h1 className="hero-headline">
            AGENTIC TRAJECTORIES<br />FOR OPTIMIZING<br />MOLECULES.
          </h1>
          <p className="hero-subheadline">
            AN OPENENV RL ENVIRONMENT FOR DRUG LEAD OPTIMIZATION.
          </p>
          <TerminalInput
            placeholder="ENTER SMILES / INITIALIZE AGENT"
            label="ENTER SMILES / INITIALIZE AGENT"
          />
        </div>
        <div className="hero-right">
          <div className="hero-grid-overlay">
            {Array.from({ length: 9 }).map((_, i) => (
              <div className="hero-grid-cell" key={i} />
            ))}
          </div>
          <DataBlock
            rows={[
              { label: 'QED_SCORE', value: '0.72' },
              { label: 'LogP', value: '2.4' },
              { label: 'SA_SCORE', value: '3.1' },
              { label: 'STATUS', value: 'OPTIMIZING', alert: true },
            ]}
          />
        </div>
      </section>

      {/* MARQUEE */}
      <MarqueeTape />

      {/* STATS */}
      <StatsGrid
        stats={[
          { value: '$2.6B', label: 'AVG DRUG COST', bgColor: '#FFFFFF', textColor: '#000000' },
          { value: '10⁶⁰', label: 'CHEMICAL SPACE', bgColor: '#7B3EFC', textColor: '#FFFFFF' },
          { value: '3', label: 'GRADED TASKS', bgColor: '#CCFF00', textColor: '#000000' },
          { value: '0.0–1.0', label: 'CONTINUOUS SCORING', bgColor: '#000000', textColor: '#FFFFFF' },
        ]}
      />

      {/* FEATURE CARDS */}
      <section className="section">
        <div className="three-col">
          <FeatureCard
            atomicNumber="1"
            symbol="In"
            elementName="Innovation"
            numberBgColor="#FF5415"
            numberTextColor="#000000"
            icon={<Grid3x3 size={48} strokeWidth={1.5} />}
            title="DUAL-MODE ACTION SPACE."
            description="Solve 'indexing hell' — the Dynamic State-Mapping Layer translates LLM site selections into RDKit atom indices. Mode 2 site enumeration with natural-language spatial descriptions."
            bgColor="#FFFFFF"
            textColor="#000000"
            className="bg-chem-light"
          />
          <FeatureCard
            atomicNumber="2"
            symbol="Ch"
            elementName="Chemistry"
            numberBgColor="#7B3EFC"
            numberTextColor="#FFFFFF"
            numberShadow="4px 4px 0px 0px #FFFFFF"
            icon={<Triangle size={48} strokeWidth={1.5} />}
            title="REAL CHEMINFORMATICS."
            description="Every modification runs through RDKit's validated chemistry engine. Chemical valency enforced. PAINS alerts detected. Lipinski Rule of 5 checked. No string manipulation — real molecular graphs."
            bgColor="#000000"
            textColor="#FFFFFF"
          />
          <FeatureCard
            atomicNumber="3"
            symbol="Sc"
            elementName="Scoring"
            numberBgColor="#000000"
            numberTextColor="#FFFFFF"
            icon={<Shield size={48} strokeWidth={1.5} />}
            title="TRAJECTORY-AWARE REWARDS."
            description="Score the entire optimization campaign, not just the final molecule. Five weighted components: Target Adherence (40%), Trajectory Quality (25%), Step Efficiency (15%), Chemical Validity (10%), Exploration Diversity (10%)."
            bgColor="#FFFFFF"
            textColor="#000000"
          />
        </div>
      </section>

      {/* DARK TERMINAL SECTION */}
      <section className="section split-section bg-chem-dark" style={{ borderColor: '#000' }}>
        <div className="split-left" style={{ borderColor: '#1A1A1A' }}>
          <h2 style={{
            fontFamily: 'var(--font-display)',
            fontSize: 'var(--text-display)',
            color: '#CCFF00',
            textShadow: '2px 2px 0 rgba(255,255,255,0.2)',
            textTransform: 'uppercase',
            lineHeight: 1.1,
            marginBottom: 'var(--space-5)',
          }}>
            MOLECULAR<br />AUTHORITY.
          </h2>
          <p style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 'var(--text-body-lg)',
            color: '#999',
            lineHeight: 1.6,
            paddingLeft: 'var(--space-4)',
            borderLeft: '2px solid #7B3EFC',
            marginBottom: 'var(--space-5)',
          }}>
            Train RL agents as autonomous medicinal chemists. Observe properties, hypothesize modifications, apply fragments, evaluate results, iterate.
          </p>
          <Button variant="secondary-dark" to="/tasks" icon={<ArrowUpRight size={18} />}>
            EXPLORE TASKS
          </Button>
        </div>
        <div className="split-right" style={{ backgroundColor: '#000000' }}>
          <TerminalWindow
            lines={[
              { text: '> initializing ATOM environment...', className: 'dim' },
              { text: '> loading fragment library [OK]', className: 'dim' },
              { text: '> scaffold: c1ccccc1 (benzene)', className: 'white' },
              { text: '> target: LogP ∈ [2.5, 3.0]', className: 'white' },
              { text: '> AGENT EPISODE STARTED', className: 'green' },
              { text: '$ agent.step(get_valid_sites)', className: 'white' },
              { text: '> sites: [{id:0, desc:"para to H"}, {id:1, desc:"meta to H"}]', className: '' },
              { text: '$ agent.step(add_fragment, "methyl", site_id=0)', className: 'white' },
              { text: '> QED: 0.44 → 0.51 (+0.07) ✓', className: 'green' },
            ]}
          />
        </div>
      </section>

      {/* COMPLIANCE TAGS */}
      <section className="section">
        <div className="tags-bar" style={{ backgroundColor: '#FFFFFF' }}>
          <Tag color="green">OPENENV SPEC COMPLIANT</Tag>
          <Tag color="black">PYDANTIC TYPED MODELS</Tag>
          <Tag color="purple">DOCKER CONTAINERIZED</Tag>
          <Tag color="orange">HF SPACE DEPLOYED</Tag>
          <Tag color="green">3 GRADED TASKS</Tag>
          <Tag color="black">DETERMINISTIC GRADERS</Tag>
        </div>
      </section>

      <Footer />
    </main>
  );
};

export default Landing;
