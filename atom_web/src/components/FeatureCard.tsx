import { ReactNode } from 'react';

interface FeatureCardProps {
  atomicNumber: string;
  symbol: string;
  elementName: string;
  numberBgColor: string;
  numberTextColor: string;
  numberShadow?: string;
  icon: ReactNode;
  title: string;
  description: string;
  bgColor: string;
  textColor: string;
  className?: string;
}

const FeatureCard = ({ atomicNumber, symbol, elementName, numberBgColor, numberTextColor, numberShadow, icon, title, description, bgColor, textColor, className = '' }: FeatureCardProps) => (
  <div className={`feature-card ${className}`} style={{ backgroundColor: bgColor, color: textColor }}>
    <div
      className="periodic-tile"
      style={{
        backgroundColor: numberBgColor,
        color: numberTextColor,
        boxShadow: numberShadow || 'var(--shadow-brutal)',
      }}
    >
      <div className="periodic-number">{atomicNumber}</div>
      <div className="periodic-symbol">{symbol}</div>
      <div className="periodic-name">{elementName}</div>
    </div>
    <div className="feature-card-content">
      <div className="feature-card-icon">{icon}</div>
      <h3 className="feature-card-title">{title}</h3>
      <p className="feature-card-desc">{description}</p>
    </div>
  </div>
);

export default FeatureCard;
