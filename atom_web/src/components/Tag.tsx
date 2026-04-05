interface TagProps {
  children: string;
  color?: 'green' | 'orange' | 'purple' | 'black' | 'red' | 'white';
}

const Tag = ({ children, color = 'black' }: TagProps) => (
  <span className={`tag tag-${color}`}>{children}</span>
);

export default Tag;
