/**
 * MoleculeViewer — Renders a SMILES string as a 2D molecule
 * using the smiles-drawer library on an HTML canvas.
 */

import { useEffect, useRef } from 'react';

// smiles-drawer doesn't have proper TS types, import as any
// @ts-ignore
import SmilesDrawer from 'smiles-drawer';

interface MoleculeViewerProps {
  smiles: string;
  width?: number;
  height?: number;
  label?: string;
}

const MoleculeViewer = ({ smiles, width = 300, height = 200, label }: MoleculeViewerProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || !smiles) return;

    const options = {
      width,
      height,
      bondThickness: 1.5,
      bondLength: 15,
      shortBondLength: 0.85,
      bondSpacing: 0.18 * 15,
      atomVisualization: 'default' as const,
      isomeric: true,
      debug: false,
      terminalCarbons: true,
      explicitHydrogens: true,
      overlapSensitivity: 0.42,
      overlapResolutionIterations: 1,
      compactDrawing: true,
      fontSizeLarge: 6,
      fontSizeSmall: 4,
      padding: 20,
      themes: {
        dark: {
          C: '#CCFF00',
          O: '#FF5415',
          N: '#7B3EFC',
          F: '#00CED1',
          Cl: '#00CED1',
          Br: '#CD853F',
          S: '#FFD700',
          P: '#FFA500',
          H: '#888888',
          BACKGROUND: '#000000',
          BOND: '#AAAAAA',
        }
      }
    };

    try {
      const drawer = new SmilesDrawer.Drawer(options);
      SmilesDrawer.parse(smiles, (tree: any) => {
        drawer.draw(tree, canvasRef.current, 'dark');
      }, () => {
        // Parse error — draw error state
        const ctx = canvasRef.current?.getContext('2d');
        if (ctx) {
          ctx.fillStyle = '#000000';
          ctx.fillRect(0, 0, width, height);
          ctx.fillStyle = '#FF5415';
          ctx.font = '14px "Fira Code", monospace';
          ctx.textAlign = 'center';
          ctx.fillText('INVALID SMILES', width / 2, height / 2);
        }
      });
    } catch {
      // Fallback
      const ctx = canvasRef.current?.getContext('2d');
      if (ctx) {
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, width, height);
        ctx.fillStyle = '#666666';
        ctx.font = '12px "Fira Code", monospace';
        ctx.textAlign = 'center';
        ctx.fillText('RENDER ERROR', width / 2, height / 2);
      }
    }
  }, [smiles, width, height]);

  if (!smiles) {
    return (
      <div className="molecule-canvas-container" style={{ width, height }}>
        <div className="molecule-empty">
          NO MOLECULE
        </div>
        {label && <div className="molecule-label">{label}</div>}
      </div>
    );
  }

  return (
    <div className="molecule-canvas-container" style={{ width: '100%' }}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="molecule-canvas"
      />
      {label && <div className="molecule-label">{label}</div>}
    </div>
  );
};

export default MoleculeViewer;
