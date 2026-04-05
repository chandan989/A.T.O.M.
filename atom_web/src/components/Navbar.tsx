import { Link, useLocation } from 'react-router-dom';
import { ArrowUpRight } from 'lucide-react';
import { useState } from 'react';
import { NavLink } from './NavLink';
import ConnectionDialog from './ConnectionDialog';
import { useAtomConnection } from '../lib/atomClient';

const Navbar = () => {
  const location = useLocation();
  const [dialogOpen, setDialogOpen] = useState(false);
  const { isConnected, status } = useAtomConnection();

  const statusColor = isConnected ? '#CCFF00' : status === 'error' ? '#FF5415' : '#666';

  return (
    <>
      <nav className="navbar" aria-label="Main navigation">
        <div className="navbar-brand">
          <Link to="/" aria-current={location.pathname === '/' ? 'page' : undefined}>
            <img src="/Logo.svg" alt="ATOM" className="navbar-logo" />
          </Link>
        </div>
        <div className="navbar-links bg-grid-light">
          <NavLink to="/environment" className="navbar-link" activeClassName="active">ENVIRONMENT</NavLink>
          <NavLink to="/tasks" className="navbar-link" activeClassName="active">TASKS</NavLink>
          <NavLink to="/architecture" className="navbar-link" activeClassName="active">ARCHITECTURE</NavLink>
          <NavLink to="/docs" className="navbar-link" activeClassName="active">DOCS</NavLink>
        </div>
        <div className="navbar-cta" onClick={() => setDialogOpen(true)} role="button" tabIndex={0}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, textTransform: 'uppercase' }}>
            {isConnected ? (
              <>
                <span className="connection-status-dot" style={{ backgroundColor: statusColor, width: 10, height: 10, display: 'inline-block' }} />
                CONNECTED
              </>
            ) : (
              <>
                INITIALIZE <ArrowUpRight size={18} />
              </>
            )}
          </span>
        </div>
      </nav>
      <ConnectionDialog isOpen={dialogOpen} onClose={() => setDialogOpen(false)} />
    </>
  );
};

export default Navbar;
