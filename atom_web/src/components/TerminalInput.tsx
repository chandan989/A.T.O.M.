import { useState } from 'react';

interface TerminalInputProps {
  placeholder?: string;
  onSubmit?: (value: string) => void;
  label?: string;
}

const TerminalInput = ({ placeholder = 'EX: USER@ATOM', onSubmit, label }: TerminalInputProps) => {
  const [value, setValue] = useState('');

  const handleSubmit = () => {
    if (onSubmit && value.trim()) {
      onSubmit(value);
      setValue('');
    }
  };

  return (
    <div>
      {label && <div className="hero-input-label">{label}</div>}
      <div className="terminal-input">
        <div className="terminal-input-prefix" aria-hidden="true">{'>_'}</div>
        <input
          type="text"
          placeholder={placeholder}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          aria-label={label || placeholder}
        />
        <button className="terminal-input-submit" onClick={handleSubmit}>EXECUTE</button>
      </div>
    </div>
  );
};

export default TerminalInput;
