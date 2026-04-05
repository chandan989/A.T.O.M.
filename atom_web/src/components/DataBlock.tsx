interface DataBlockRow {
  label: string;
  value: string;
  alert?: boolean;
}

interface DataBlockProps {
  rows: DataBlockRow[];
  liveLabel?: string;
  secId?: string;
}

const DataBlock = ({ rows, liveLabel = 'Live Node', secId = '0x9F' }: DataBlockProps) => (
  <div className="data-block">
    <div className="data-block-header">
      <span className="data-block-live">{liveLabel}</span>
      <span className="data-block-id">SEC_ID: {secId}</span>
    </div>
    {rows.map((row, i) => (
      <div className="data-block-row" key={i}>
        <span>{`> ${row.label}`}</span>
        <span className={`data-block-value ${row.alert ? 'alert' : ''}`}>{row.value}</span>
      </div>
    ))}
  </div>
);

export default DataBlock;
