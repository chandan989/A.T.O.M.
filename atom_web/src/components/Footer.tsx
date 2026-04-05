import { Link } from 'react-router-dom';
import { ArrowUpRight } from 'lucide-react';

const Footer = () => (
  <footer className="footer">
    <div className="footer-brand">
      <div className="footer-brand-name">
        <img src="/Logo.svg" alt="ATOM" className="footer-logo" />
      </div>
      <p className="footer-brand-desc">
        "The underlying architecture for molecular optimization."
      </p>
      <div className="footer-brand-copy">
        © 2026 TEAM A.T.O.M. ALL RIGHTS RESERVED.
      </div>
    </div>
    <div className="footer-nav">
      <div className="footer-nav-col">
        <div className="footer-nav-title">Index_</div>
        <Link to="/environment" className="footer-nav-link">ENVIRONMENT</Link>
        <Link to="/tasks" className="footer-nav-link">TASKS</Link>
        <Link to="/architecture" className="footer-nav-link">ARCHITECTURE</Link>
        <Link to="/docs" className="footer-nav-link">DOCUMENTATION</Link>
      </div>
      <div className="footer-nav-col">
        <div className="footer-nav-title">Social_</div>
        <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="footer-nav-link">
          GITHUB <ArrowUpRight size={14} style={{ display: 'inline', verticalAlign: 'middle' }} />
        </a>
        <a href="https://huggingface.co" target="_blank" rel="noopener noreferrer" className="footer-nav-link">
          HF SPACE <ArrowUpRight size={14} style={{ display: 'inline', verticalAlign: 'middle' }} />
        </a>
        <a href="https://discord.com" target="_blank" rel="noopener noreferrer" className="footer-nav-link">
          DISCORD <ArrowUpRight size={14} style={{ display: 'inline', verticalAlign: 'middle' }} />
        </a>
      </div>
    </div>
  </footer>
);

export default Footer;
