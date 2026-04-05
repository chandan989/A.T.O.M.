interface TerminalLine {
  text: string;
  className?: string;
}

interface TerminalWindowProps {
  lines: TerminalLine[];
  title?: string;
}

const TerminalWindow = ({ lines, title = 'root@atom-protocol' }: TerminalWindowProps) => (
  <div className="terminal-window">
    <div className="terminal-header">
      <span className="terminal-header-title">{title}</span>
      <div className="terminal-header-controls">
        <div className="terminal-control" />
        <div className="terminal-control" />
        <div className="terminal-control solid" />
      </div>
    </div>
    <div className="terminal-body">
      {lines.map((line, i) => (
        <div key={i} className={`terminal-line ${line.className || ''}`}>{line.text}</div>
      ))}
      <div className="terminal-line">
        <span className="terminal-cursor">$ ▌</span>
      </div>
    </div>
  </div>
);

export default TerminalWindow;
