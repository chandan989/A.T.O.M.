<div align="center">
  <img src="../Logo.svg" alt="A.T.O.M. Logo" width="220" />

# ATOM Web Frontend
</div>

This directory contains the source code for the `atom_web` frontend, a modern React-based web application designed to visually interact with and explore the ATOM (Agentic Trajectories for Optimizing Molecules) reinforcement learning environment.

It provides researchers, chemists, and ML engineers with a clean, responsive UI to visualize molecular structures, track optimization trajectories, and observe an AI agent's step-by-step decision-making process in real-time.

## Tech Stack & Architecture

The frontend is built using a modern, high-performance web stack:

- **Framework:** React 18
- **Build Tool:** Vite (for fast HMR and optimized production builds)
- **Styling:** Tailwind CSS (utility-first CSS for rapid UI development)
- **Routing:** React Router (for SPA navigation)
- **Components:** Radix UI / shadcn/ui (accessible, customizable unstyled components)
- **Data Fetching:** TanStack Query (React Query) for state management and API synchronization
- **Language:** TypeScript
- **Package Manager:** Bun (fast dependency installation and script execution)

## Project Structure

```text
atom_web/
├── public/                 # Static assets (images, favicon, etc.)
├── src/                    # Main source code
│   ├── components/         # Reusable React components (UI elements, molecular visualizers)
│   ├── hooks/              # Custom React hooks (e.g., useAtomWebSocket, useTrajectory)
│   ├── pages/              # Route-level components (Dashboard, Task Selection, Settings)
│   ├── lib/                # Utility functions, API clients, and constants
│   ├── App.tsx             # Root application component
│   └── main.tsx            # Application entry point
├── package.json            # Project dependencies and scripts
├── vite.config.ts          # Vite bundler configuration
├── tailwind.config.ts      # Tailwind CSS theme and styling configuration
└── tsconfig.json           # TypeScript compiler options
```


## UI Layout Overview

```text
┌─────────────────────────────────────────────────────────────┐
│ ⚛️ A.T.O.M. Dashboard                  [Task: 3 - Hard] ⚙️  │
├──────────────────────┬──────────────────────────────────────┤
│ ┌──────────────────┐ │ ┌──────────────────────────────────┐ │
│ │                  │ │ │  Trajectory Optimization Graph   │ │
│ │                  │ │ │                                  │ │
│ │   Current        │ │ │   📈 LogP  📉 QED  📉 MW         │ │
│ │   Molecule       │ │ │                                  │ │
│ │   Renderer       │ │ └──────────────────────────────────┘ │
│ │                  │ │ ┌──────────────────────────────────┐ │
│ │   (RDKit SVG)    │ │ │  Agent Action Log                │ │
│ │                  │ │ │  > step(get_valid_sites)         │ │
│ │                  │ │ │  < Found 5 valid sites           │ │
│ │                  │ │ │  > step(add_fragment, site_2...) │ │
│ │                  │ │ │  < Success. QED +0.05            │ │
│ └──────────────────┘ │ └──────────────────────────────────┘ │
├──────────────────────┴──────────────────────────────────────┤
│  Rubric Score: 0.85 [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░]                  │
│  Adherence: 0.9 | Trajectory: 0.8 | Efficiency: 0.9         │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

1. **Real-time Molecular Visualization:** Integrates with molecular rendering libraries (or lightweight SVG generators via RDKit backend) to display the 2D structure of the current molecule.
2. **Trajectory Tracking:** Visualizes the agent's progress over time. Graphs display property changes (LogP, QED, MW) across sequential steps, allowing users to see if the agent is converging toward the Target Product Profile (TPP) or diverging.
3. **Action Logs & Feedback:** A live updating log of the agent's actions (e.g., `get_valid_sites`, `add_fragment`, `mutate_atom`) and the environment's corresponding textual feedback.
4. **Task Dashboard:** A UI to select between the 4 difficulty tasks (Easy, Medium, Hard, Extreme/Dynamic) and initialize a new episode against the backend server.
5. **Score Breakdown:** A detailed visual breakdown of the `RubricEngine`'s final score composition (Target Adherence, Trajectory Quality, Step Efficiency, Validity, Diversity).

## Getting Started

### Prerequisites

- Node.js (v18+)
- [Bun](https://bun.sh/) (recommended for fastest installation, though `npm` or `yarn` will also work)

### Installation

Navigate to the `atom_web` directory and install dependencies:

```bash
cd atom_web

# Install dependencies using Bun
bun install
```

### Development Server

To start the Vite development server with Hot Module Replacement (HMR):

```bash
# Start the dev server
bun run dev
```

The application will typically be available at `http://localhost:8080` (or another port specified in the Vite output).

### Connecting to the ATOM Server

The frontend is designed to communicate with the FastAPI backend located in the `../server` directory. Ensure the backend server is running concurrently.

```bash
# In a separate terminal, start the backend server
cd ../server
python app.py
```

By default, the Vite proxy or API client in `src/lib/api.ts` should be configured to point to `http://localhost:8000` (the default FastAPI port). If your backend is running on a different port or host, update the configuration accordingly.

## Building for Production

To build the application for production deployment:

```bash
bun run build
```

This will generate an optimized, minified bundle in the `dist/` directory, ready to be served by any static file server (Nginx, Vercel, Netlify, or integrated into a FastAPI static route).

## Linting and Testing

The project uses ESLint for code quality and Vitest/Playwright for testing.

```bash
# Run ESLint to check for code style issues
bun run lint

# Run unit tests (Vitest)
bun run test

# Run End-to-End tests (Playwright)
bun run e2e
```

## Extending the UI

When adding new features or components:
1. Ensure components are placed in `src/components/`.
2. Use Tailwind utility classes for styling. Try to avoid writing custom CSS unless absolutely necessary.
3. Leverage shadcn/ui components (if installed in `components/ui`) for consistent design patterns.
4. Keep API calls encapsulated within custom hooks using TanStack Query to manage loading and error states cleanly.
