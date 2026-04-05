import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import TaskCard from '../components/TaskCard';
import SectionHeader from '../components/SectionHeader';
import DataTable from '../components/DataTable';
import { Target, RefreshCw, LineChart, ListOrdered } from 'lucide-react';
import { tasks } from '../data/mockTasks';
import { rewardComponents } from '../data/mockChartData';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const Tasks = () => (
  <main>
    <Navbar />

    <section className="section bg-chem-dark">
      <div className="page-header">
        <h1 className="page-header-title">TASKS & GRADERS</h1>
        <p className="page-header-subtitle">
          Three evaluation tasks with escalating difficulty. Easy → Medium → Hard.
        </p>
      </div>
    </section>

    {/* TASK CARDS */}
    <section className="section bg-chem-light">
      <div className="three-col" style={{ padding: 'var(--space-5)', gap: 'var(--space-5)' }}>
        {tasks.map(task => (
          <TaskCard key={task.id} task={task} />
        ))}
      </div>
    </section>

    {/* REWARD FUNCTION */}
    <section className="section bg-chem-dark" style={{ color: '#FFFFFF' }}>
      <div className="content-section">
        <SectionHeader title="REWARD FUNCTION" dark subtitle="Multi-objective reinforcement learning reward breakdown" />
        <div className="two-col" style={{ marginTop: 'var(--space-5)', border: '4px solid #333', backgroundColor: '#000', boxShadow: '8px 8px 0px 0px #000' }}>
          
          <div style={{ padding: 'var(--space-5)', borderRight: '2px dashed #333', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', overflow: 'hidden' }}>
            {/* Cool background overlay */}
            <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(204, 255, 0, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(204, 255, 0, 0.05) 1px, transparent 1px)', backgroundSize: '20px 20px', pointerEvents: 'none' }} />
            <div style={{ position: 'absolute', top: 0, left: 0, padding: 'var(--space-2)', fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--color-green)' }}>[RADAR_ACTIVE]</div>
            <div style={{ position: 'absolute', bottom: 0, right: 0, padding: 'var(--space-2)', fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--color-green)' }}>[SYS_OPTIMAL]</div>

            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={rewardComponents.map(c => ({ name: c.name, value: c.weight }))}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={140}
                  dataKey="value"
                  stroke="#000"
                  strokeWidth={4}
                >
                  {rewardComponents.map((c, i) => (
                    <Cell key={i} fill={c.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#000',
                    border: '2px solid var(--color-green)',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '14px',
                    color: '#FFF',
                    borderRadius: 0,
                    boxShadow: '4px 4px 0px 0px var(--color-green)'
                  }}
                  itemStyle={{ color: 'var(--color-green)' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          <div style={{ padding: '0', backgroundColor: '#1A1A1A' }}>
            <DataTable
              dark
              headers={['Component', 'Weight', 'Description']}
              rows={rewardComponents.map(c => [
                c.name,
                `${c.weight}%`,
                c.description,
              ])}
            />
          </div>
        </div>
      </div>
    </section>

    {/* GRADER GUARANTEES */}
    <section className="section bg-chem-light">
      <div className="content-section">
        <SectionHeader title="GRADER GUARANTEES" subtitle="Rigorous properties of the chemical environment" />
        <div className="two-by-two" style={{ marginTop: 'var(--space-5)' }}>
          {[
            { title: 'DETERMINISTIC', desc: 'Same trajectory → same score. No randomness in grading.', Icon: Target },
            { title: 'REPRODUCIBLE', desc: 'Multiple runs yield identical results across environments.', Icon: RefreshCw },
            { title: 'CONTINUOUS', desc: 'Floats in [0.0, 1.0], never binary pass/fail.', Icon: LineChart },
            { title: 'PROGRESSIVE', desc: 'Score 0.9 on Task 1 may score 0.3 on Task 3.', Icon: ListOrdered },
          ].map((item, index) => (
            <div key={item.title} style={{
              border: 'var(--border-thick) solid #000',
              boxShadow: '6px 6px 0px 0px #000',
              padding: 'var(--space-5)',
              backgroundColor: '#FFF',
              position: 'relative',
              transition: 'transform var(--transition-fast) linear, box-shadow var(--transition-fast) linear'
            }}
            onMouseEnter={(e) => { e.currentTarget.style.transform = 'translate(-2px, -2px)'; e.currentTarget.style.boxShadow = '8px 8px 0px 0px var(--color-purple)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = '6px 6px 0px 0px #000'; }}
            >
              <div style={{ position: 'absolute', top: 0, right: 0, backgroundColor: '#000', color: '#FFF', width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'var(--font-mono)', fontWeight: 'bold' }}>
                0{index + 1}
              </div>
              <div style={{ marginBottom: 'var(--space-3)', color: 'var(--color-black)' }}>
                <item.Icon size={40} strokeWidth={1.5} />
              </div>
              <h3 style={{
                fontFamily: 'var(--font-sans)',
                fontSize: 'var(--text-body-lg)',
                fontWeight: 800,
                textTransform: 'uppercase' as const,
                marginBottom: 'var(--space-2)',
                color: 'var(--color-purple)'
              }}>
                {item.title}
              </h3>
              <p style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 'var(--text-mono)',
                lineHeight: 1.6,
                color: '#333',
              }}>
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>

    <Footer />
  </main>
);

export default Tasks;
