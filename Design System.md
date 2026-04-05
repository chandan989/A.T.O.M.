# ATOM Design System

## 1. 🎨 Brand Identity
**Personality Traits:** Unapologetic, Cryptographic, Brutalist, Transparent, Sovereign.
**Design Principles:** * **Structure is Surface:** Expose the grid. Let the user see the math.
* **Digital Brutalism:** Sharp edges, high contrast, zero fluff. Function dictates form.
* **Typographic Tension:** Mix highly legible modern sans-serif with raw, pixelated display types to bridge the gap between protocol and user.
**Voice & Tone:** Direct, authoritative, and concise. No marketing speak. Commands and statements (e.g., "OWN YOUR DIGITAL IDENTITY", "NO PERMISSION REQUIRED").

---

## 2. 🌈 Color System
Built for maximum contrast. The system uses absolute black/white as staging grounds for aggressive, neon highlight colors.

* **Primary Palette:** * Atom Purple: `#7B3EFC` (Main action, primary identity)
  * Atom Black: `#000000` (Dark mode background, high-contrast text)
  * Atom White: `#FFFFFF` (Light mode background, high-contrast text)
* **Semantic Palette:**
  * Highlight Green (Success/Accent): `#CCFF00`
  * Warning Orange (Alert/Accent): `#FF5415`
  * Mute Gray (Gridlines/Subtle borders): `#E5E5E5` (Light), `#1A1A1A` (Dark)
* **Contrast Ratios:** All primary text passes WCAG AAA (Black on White, White on Black). Neon colors on black/white surfaces pass AA minimums for large text and UI components.

---

## 3. ✍️ Typography
**Font Stacks:**
* **Display / Logo:** `VT323`, `Press Start 2P`, or custom pixel/bitmap font. (Used for brand marks, decorative massive headers).
* **Sans-Serif (Body & Headings):** `Inter`, `Space Grotesk`, or `Helvetica Neue`. (Clean, geometric, highly legible. All caps for primary marketing headers).
* **Monospace (Data & Inputs):** `Fira Code` or `Roboto Mono`. (Used for usernames, code snippets, input placeholders).

**Type Scale (Desktop):**
* **Display:** 64px / 1.1 line-height / -0.02em tracking / All Caps
* **H1:** 48px / 1.1 line-height / -0.02em tracking / All Caps
* **H2:** 32px / 1.2 line-height / -0.01em tracking
* **Body Lg:** 20px / 1.5 line-height / Normal tracking
* **Body:** 16px / 1.5 line-height / Normal tracking
* **Mono / Tag:** 14px / 1.4 line-height / 0.05em tracking

---

## 4. 📐 Spacing & Layout (Full-Bleed Architecture)
**The Grid is Visible and Infinite.**
* **Base Unit:** 8px.
* **Spacing Scale:** 0, 4, 8, 16, 24, 32, 48, 64, 96, 128.
* **Containers (Zero Padding):** `100vw`. There are **no maximum width constraints** and **zero outer horizontal padding** (`px-0`). The layout must hit the absolute left and right edges of the browser window.
* **Background Patterns:** Content strictly sits on visible tiling patterns spanning edge-to-edge. Use the square grids (`.bg-grid-light` / `dark`) or the chemical hexagon networks (`.bg-chem-light` / `dark`) to enforce the molecular computing aesthetic.

---

## 5. 🔲 Elevation & Shadow
**Strictly Flat.**
* **Shadow Scale:** NONE.
* **Elevation:** Visual hierarchy is established through stark color contrast and 1px solid borders, *never* through soft drop shadows. If depth is required, use solid, non-blurred offset shapes (e.g., a solid black box translated 4px down and 4px right beneath a white card).

---

## 6. 🔵 Border & Radius
* **Border Radius:** `0px`. Absolutely no rounded corners. Everything is a sharp right angle. **This includes chemical motifs like atoms and molecules.** "Brutalist Chemistry" demands solid square 'atoms' and rigid, straight 'bonds'.
* **Border Widths:** `1px` (for structural grids), `2px` (for component definitions like buttons or active inputs), `4px` (for heavy emphasis).
* **Chemical Double-Bonds:** Primary layout dividers should utilize `var(--border-thick) double var(--color-black)` borders to conceptually mimic structural double-bonds.

---

## 7. 🧩 Component Specifications

**Periodic Table Tiles**
* **Purpose:** Replaces generic numbered list badges (e.g., "01", "1.") with chemical element styling.
* **Anatomy:** Atomic number in the top-left (10px Mono), massive primary symbol centered (36px Display), and the full trait/element name docked at the bottom (8px Mono, uppercase).

**Feature & Data Cards**
* Structured inside heavy 2px black boxes, utilizing solid translated drop-shadows. Headers may use Periodic Table Tiles to identify the feature rank.

**Button**
* **Variants:** * *Primary:* Atom Purple background, Black/White text.
  * *Secondary:* Transparent background, 2px border, high-contrast text.
* **States:** Hover (Invert colors or shift background to highlight green/orange), Active (translate Y +2px).
* **Do/Don't:** DO use all-caps for button labels. DON'T add rounded corners or internal padding that breaks the grid rhythm.

**Input Field**
* **Anatomy:** Container, Prefix icon/logo (e.g., pixelated 'A'), Input area.
* **Style:** Resembles a terminal command line. Monospace font for the input text. Solid background (Purple or Black) with contrasting monospace placeholder (e.g., `ex: user@atom`). Edge-to-edge internal content without side margins.

**Tags / Badges**
* **Style:** Sharp rectangles resembling text-highlighter marks. Backgrounds in Neon Green, Orange, or Gray. Monospace text inside.

---

## 8. 🎞️ Motion & Animation
* **Style:** Snappy, instantaneous, mechanical.
* **Duration:** Fast (100ms) or Instant (0ms).
* **Easing:** Linear or sharp step-functions.
* **Anti-pattern:** No slow, fluid, or "bouncy" spring animations. Motion should feel like a screen refreshing or a command executing.

---

## 9. 🖼️ Iconography
* **Style:** Sharp, geometric, or pixelated. Heavy stroke widths (2px+).
* **Icons:** Arrows must be sharp 90-degree angles (`↗`, `↓`), never rounded soft arrows. Logos/Marks should utilize the pixel-grid aesthetic.

---

## 10. ♿ Accessibility Standards
* **Target:** WCAG AA (AAA for core text).
* **Focus Management:** 2px solid highlight green (`#CCFF00`) outline with 2px offset for keyboard focus.
* **Touch Targets:** Minimum 48x48px for all interactive elements to balance the dense grid look with usability.

---

## 11. 🚫 Anti-Patterns
* **DON'T** wrap the main content in a container with horizontal padding or `max-width`. The layout must bleed off the screen.
* **DON'T** use border-radius anywhere. Not on buttons, not on modals, not on images.
* **DON'T** use drop-shadows, blurs, or gradients. Colors must be solid and flat.
* **DON'T** use soft, conversational language. Keep copy punchy and declarative.