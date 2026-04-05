interface CodeBlockProps {
  children: string;
}

const CodeBlock = ({ children }: CodeBlockProps) => (
  <pre className="code-block">{children}</pre>
);

export default CodeBlock;
