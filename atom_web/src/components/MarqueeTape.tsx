const phrases = ['TRANSPARENT.', 'SOVEREIGN.', 'UNAPOLOGETIC.', 'OPTIMIZED.', 'VALIDATED.'];
const repeated = [...phrases, ...phrases, ...phrases, ...phrases];

const MarqueeTape = () => (
  <div className="marquee-tape" aria-hidden="true">
    <div className="marquee-inner">
      {repeated.map((phrase, i) => (
        <span key={i}>{phrase}</span>
      ))}
    </div>
  </div>
);

export default MarqueeTape;
