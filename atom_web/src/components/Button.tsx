import { ReactNode } from 'react';
import { Link } from 'react-router-dom';

interface ButtonProps {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'secondary-dark';
  to?: string;
  onClick?: () => void;
  icon?: ReactNode;
  className?: string;
  disabled?: boolean;
}

const Button = ({ children, variant = 'primary', to, onClick, icon, className = '', disabled }: ButtonProps) => {
  const cls = `btn btn-${variant} ${className}`;

  if (to) {
    return (
      <Link to={to} className={cls}>
        {children} {icon}
      </Link>
    );
  }

  return (
    <button className={cls} onClick={onClick} disabled={disabled}>
      {children} {icon}
    </button>
  );
};

export default Button;
