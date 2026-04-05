import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import SectionHeader from '../components/SectionHeader';
import CodeBlock from '../components/CodeBlock';
import DataTable from '../components/DataTable';
import Tag from '../components/Tag';
import { baselineScores } from '../data/mockChartData';

const Docs = () => (
  <main>
    <Navbar />

    <section className="section bg-chem-dark">
      <div className="page-header">
        <h1 className="page-header-title">DOCUMENTATION</h1>
      </div>
    </section>

    {/* QUICK START */}
    <section className="section bg-chem-light">
      <div className="content-section">
        <SectionHeader title="QUICK START" />
        <div style={{ position: 'relative', display: 'flex', flexDirection: 'column', gap: 'var(--space-6)', marginTop: 'var(--space-5)', paddingLeft: 'var(--space-6)' }}>
          {/* Connecting Line */}
          <div style={{ position: 'absolute', top: '40px', bottom: '40px', left: '38px', width: '4px', backgroundColor: '#000', zIndex: 0 }} />
          
          <div className="step-card" style={{ position: 'relative', zIndex: 1, marginLeft: 'var(--space-4)' }}>
            <div style={{ position: 'absolute', left: '-80px', top: '20px' }}>
              <div className="periodic-tile" style={{ backgroundColor: '#CCFF00', color: '#000', marginBottom: 0, boxShadow: '4px 4px 0px 0px #000' }}>
                <div className="periodic-number">1</div>
                <div className="periodic-symbol">Cl</div>
                <div className="periodic-name">CLONE</div>
              </div>
            </div>
            <div className="step-card-body" style={{ backgroundColor: '#FFF' }}>
              <h4 style={{ fontSize: '20px', color: 'var(--color-purple)' }}>CLONE & INSTALL</h4>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', marginBottom: 'var(--space-3)', color: '#666' }}>Clone the repo and set up Python dependencies.</p>
              <CodeBlock>{`git clone https://github.com/team-atom/atom-env.git
cd atom-env
pip install -r requirements.txt`}</CodeBlock>
            </div>
          </div>
          
          <div className="step-card" style={{ position: 'relative', zIndex: 1, marginLeft: 'var(--space-4)' }}>
            <div style={{ position: 'absolute', left: '-80px', top: '20px' }}>
              <div className="periodic-tile" style={{ backgroundColor: '#FF5415', color: '#FFF', marginBottom: 0, boxShadow: '4px 4px 0px 0px #000' }}>
                <div className="periodic-number">2</div>
                <div className="periodic-symbol">Ru</div>
                <div className="periodic-name">RUN</div>
              </div>
            </div>
            <div className="step-card-body" style={{ backgroundColor: '#FFF' }}>
              <h4 style={{ fontSize: '20px', color: 'var(--color-purple)' }}>RUN SERVER</h4>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', marginBottom: 'var(--space-3)', color: '#666' }}>Start the FastAPI environment server locally.</p>
              <CodeBlock>{`uvicorn server:app --host 0.0.0.0 --port 8000`}</CodeBlock>
            </div>
          </div>
          
          <div className="step-card" style={{ position: 'relative', zIndex: 1, marginLeft: 'var(--space-4)' }}>
            <div style={{ position: 'absolute', left: '-80px', top: '20px' }}>
              <div className="periodic-tile" style={{ backgroundColor: '#7B3EFC', color: '#FFF', marginBottom: 0, boxShadow: '4px 4px 0px 0px #000' }}>
                <div className="periodic-number">3</div>
                <div className="periodic-symbol">In</div>
                <div className="periodic-name">INFER</div>
              </div>
            </div>
            <div className="step-card-body" style={{ backgroundColor: '#FFF' }}>
              <h4 style={{ fontSize: '20px', color: 'var(--color-purple)' }}>RUN INFERENCE</h4>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', marginBottom: 'var(--space-3)', color: '#666' }}>Execute the dual-agent actor-critic loop against the simulated environment.</p>
              <CodeBlock>{`export API_BASE_URL=http://localhost:8000
export MODEL_NAME=gpt-4o
export HF_TOKEN=hf_xxxxx

python inference.py`}</CodeBlock>
            </div>
          </div>
        </div>
      </div>
    </section>

    {/* ENV VARS */}
    <section className="section bg-chem-dark" style={{ color: '#FFFFFF' }}>
      <div className="content-section">
        <SectionHeader title="ENVIRONMENT VARIABLES" dark />
        <DataTable
          dark
          headers={['Variable', 'Description', 'Example']}
          rows={[
            ['API_BASE_URL', 'Base URL of the LLM API endpoint', 'https://api.openai.com/v1'],
            ['MODEL_NAME', 'LLM model identifier', 'gpt-4o'],
            ['HF_TOKEN', 'HuggingFace API token for LLM access', 'hf_xxxxx'],
            ['ATOM_API_KEY', 'API key for the ATOM server (printed on boot)', 'a1b2c3...'],
            ['ATOM_SERVER_URL', 'URL of the running ATOM server', 'http://localhost:8000'],
          ]}
        />
      </div>
    </section>

    {/* DOCKER */}
    <section className="section bg-chem-light">
      <div className="content-section">
        <SectionHeader title="DOCKER DEPLOYMENT" />
        <CodeBlock>{`docker build -t atom-env .
docker run -p 8000:8000 atom-env`}</CodeBlock>
        <div style={{ marginTop: 'var(--space-4)', display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
          <Tag color="purple">FASTAPI SERVER</Tag>
          <Tag color="green">RDKIT ENGINE</Tag>
          <Tag color="black">GRADING RUBRIC</Tag>
          <Tag color="orange">FRAGMENT LIBRARY</Tag>
        </div>
      </div>
    </section>

    {/* BASELINE SCORES */}
    <section className="section bg-chem-dark" style={{ color: '#FFFFFF' }}>
      <div className="content-section">
        <SectionHeader title="BASELINE SCORES" dark />
        <DataTable
          dark
          headers={['Task', 'Difficulty', 'Score', 'Notes']}
          rows={baselineScores.map(b => [
            b.task,
            <Tag key={b.difficulty} color={b.difficulty === 'easy' ? 'green' : b.difficulty === 'medium' ? 'orange' : 'red'}>{b.difficulty}</Tag>,
            <span key={b.score} style={{ fontFamily: 'var(--font-sans)', fontSize: 'var(--text-h2)', fontWeight: 800, color: b.color }}>{b.score}</span>,
            b.notes,
          ])}
        />
      </div>
    </section>

    {/* REPO STRUCTURE */}
    <section className="section bg-chem-light">
      <div className="content-section">
        <SectionHeader title="REPOSITORY STRUCTURE" />
        <div className="code-block file-tree" style={{ marginTop: 'var(--space-4)', position: 'relative' }}>
          <div style={{ position: 'absolute', top: 0, right: 0, backgroundColor: 'var(--color-green)', color: '#000', padding: 'var(--space-1) var(--space-2)', fontWeight: 'bold' }}>FILE TREE</div>
{`ATOM/
├── openenv.yaml              # OpenEnv manifest
├── inference.py              # Baseline dual-agent inference script
├── models.py                 # Pydantic Action & Observation models
├── Dockerfile                # Docker container for HF Spaces
├── README.md
│
├── server/
│   ├── app.py                # FastAPI wrapper (CORS, auth, WebSocket)
│   ├── auth.py               # API key generation & validation
│   ├── atom_environment.py   # OpenEnv Environment class
│   ├── requirements.txt
│   │
│   ├── chemistry/
│   │   ├── engine.py         # RDKit property computation & validation
│   │   ├── state_mapper.py   # Dynamic site_id ↔ atom index mapping
│   │   └── fragments.py      # 77 curated fragment library
│   │
│   └── rubrics/
│       ├── evaluator.py      # Task definitions & 5-component grader
│       └── trajectory.py     # Trajectory quality tracker
│
└── atom_web/                 # React frontend (Vite + TypeScript)
    └── src/
        ├── pages/            # Landing, Environment, Tasks, Playground...
        ├── components/       # Navbar, ConnectionDialog, MoleculeViewer...
        ├── hooks/            # useAtomSession (WebSocket observer)
        └── lib/              # atomClient (API + React context)`}
        </div>
      </div>
    </section>

    {/* INFRASTRUCTURE */}
    <section className="section bg-chem-dark" style={{ color: '#FFFFFF' }}>
      <div className="content-section">
        <SectionHeader title="INFRASTRUCTURE COMPLIANCE" dark />
        <DataTable
          dark
          headers={['Requirement', 'Status', 'Detail']}
          rows={[
            ['Runtime', <Tag key="r" color="green">✓ COMPLIANT</Tag>, 'Python 3.11+ with RDKit, FastAPI'],
            ['Resources', <Tag key="re" color="green">✓ COMPLIANT</Tag>, '< 2GB RAM, no GPU required'],
            ['OpenAI Client', <Tag key="o" color="green">✓ COMPLIANT</Tag>, 'Uses openai-compatible API client'],
            ['Env Vars', <Tag key="e" color="green">✓ COMPLIANT</Tag>, 'API_BASE_URL, MODEL_NAME, HF_TOKEN'],
            ['Script Location', <Tag key="s" color="green">✓ COMPLIANT</Tag>, 'inference.py at repository root'],
          ]}
        />
      </div>
    </section>

    <Footer />
  </main>
);

export default Docs;
