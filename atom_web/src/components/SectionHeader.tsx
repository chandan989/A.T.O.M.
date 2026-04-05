interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  dark?: boolean;
  green?: boolean;
}

const SectionHeader = ({ title, subtitle, dark, green }: SectionHeaderProps) => (
  <div className="section-header">
    <h2
      className="section-header-title"
      style={{
        color: green ? '#CCFF00' : dark ? '#FFFFFF' : '#000000',
        textShadow: dark ? '2px 2px 0 rgba(255,255,255,0.2)' : undefined,
      }}
    >
      {title}
    </h2>
    {subtitle && (
      <p
        className="section-header-subtitle"
        style={{ color: dark ? '#999' : '#666' }}
      >
        {subtitle}
      </p>
    )}
  </div>
);

export default SectionHeader;
