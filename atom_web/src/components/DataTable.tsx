interface DataTableProps {
  headers: string[];
  rows: (string | React.ReactNode)[][];
  dark?: boolean;
}

const DataTable = ({ headers, rows, dark }: DataTableProps) => (
  <table className="data-table" style={{ color: dark ? '#ccc' : '#000' }}>
    <thead>
      <tr>
        {headers.map((h, i) => (
          <th key={i} style={{ borderColor: dark ? '#1A1A1A' : '#000' }}>{h}</th>
        ))}
      </tr>
    </thead>
    <tbody>
      {rows.map((row, i) => (
        <tr key={i}>
          {row.map((cell, j) => (
            <td key={j}>{cell}</td>
          ))}
        </tr>
      ))}
    </tbody>
  </table>
);

export default DataTable;
