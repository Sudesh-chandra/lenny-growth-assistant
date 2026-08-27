# Design Document - Lenny Growth Assistant

## 1. UI/UX Principles

### Design Philosophy
**"Clean, classic, timeless"** - Inspired by the understated elegance of ChatGPT, Claude, and Linear.

### Core Principles

1. **Clarity Over Decoration**
   - Every element serves a purpose
   - No gratuitous gradients, glows, or animations
   - Content is the hero, not the chrome

2. **Progressive Disclosure**
   - Show only what's needed, when it's needed
   - Advanced options hidden behind clear affordances
   - Reduce cognitive load for new users

3. **Professional Aesthetic**
   - Dark mode by default (reduces eye strain for long sessions)
   - Classic color palette (deep slate/zinc, not neon purple)
   - Official brand logos (not generic icons)

4. **Responsive Feedback**
   - Streaming responses (tokens appear as they generate)
   - Clear loading states (no ambiguous waiting)
   - Immediate error feedback with actionable messages

5. **Accessibility First**
   - Keyboard navigation throughout
   - Screen reader support (ARIA labels)
   - Sufficient color contrast (WCAG 2.1 AA)
   - Focus indicators on interactive elements

---

## 2. Information Architecture

### Top-Level Structure

```
┌─────────────────────────────────────────────────────────┐
│                    LENNY GROWTH ASSISTANT                │
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│   SIDEBAR    │            MAIN CHAT AREA                │
│              │                                          │
│  • New Chat  │  ┌────────────────────────────────────┐ │
│              │  │                                    │ │
│  • Sessions  │  │   Welcome Screen / Chat History    │ │
│    - List    │  │                                    │ │
│    - Search  │  │                                    │ │
│              │  │                                    │ │
│              │  │                                    │ │
│              │  └────────────────────────────────────┘ │
│              │                                          │
│  • Settings  │  ┌────────────────────────────────────┐ │
│    - Model   │  │                                    │ │
│    - Theme   │  │        Input Area                  │ │
│              │  │                                    │ │
│              │  └────────────────────────────────────┘ │
│              │                                          │
└──────────────┴──────────────────────────────────────────┘
```

### Sidebar Components

1. **New Chat Button**
   - Primary action (always visible)
   - Keyboard shortcut: ⌘K / Ctrl+K
   - Understated styling (dark background, subtle border)

2. **Session List**
   - Shows last 20 sessions
   - Auto-generated titles (first 50 chars of first query)
   - Sorted by last activity (most recent first)
   - Click to resume session
   - Hover to reveal delete button

3. **Model Indicator**
   - Shows current LLM provider (OpenAI, Anthropic, etc.)
   - Official brand logo (not generic icon)
   - Click to switch provider (dropdown)

### Main Chat Area

1. **Welcome Screen** (empty state)
   - Lenny monogram logo (minimalist "L")
   - Greeting: "Hello, I'm Lenny's Growth Assistant"
   - Subtitle: "Ask about product management, growth strategies, or request artifacts"
   - Starter cards (3-4 example queries)

2. **Chat History** (active session)
   - Messages displayed in chronological order
   - User messages: right-aligned, dark background
   - Assistant messages: left-aligned, lighter background
   - Citations: below assistant messages
   - Artifacts: rendered in sandboxed iframe

3. **Input Area**
   - Textarea (auto-expands with content)
   - Send button (disabled when empty)
   - Keyboard shortcut: Enter to send, Shift+Enter for newline
   - Placeholder: "Ask about product management, growth strategies, or request artifacts..."

---

## 3. Key Interaction States

### State 1: Empty State (Welcome Screen)

**Visual**:
- Centered Lenny monogram (64x64px)
- Greeting text (large, bold)
- Subtitle (smaller, muted)
- 3-4 starter cards (grid layout)

**Behavior**:
- Click starter card → populates input with example query
- Type query → enables send button
- Send query → creates new session, transitions to chat history

**Starter Cards**:
1. "How do top companies measure Product-Market Fit?"
2. "What growth loops work for B2B SaaS?"
3. "Write a PRD for a referral program"
4. "Explain 'Jobs to be Done' with examples"

### State 2: Loading (Waiting for Response)

**Visual**:
- Streaming indicator (animated "L" monogram)
- Text: "Thinking..." or "Searching transcripts..."
- Input disabled (prevent duplicate queries)

**Behavior**:
- Tokens appear as they generate (streaming)
- User can see progress (not stuck waiting)
- Cancel button (stop generation)

### State 3: Response Complete

**Visual**:
- Full response text with [Source N] citations
- Citation list below response
- Each citation: source, guest, snippet, relevance score
- Input re-enabled for follow-up query

**Behavior**:
- Click citation → expand to show full details
- Copy button on response (one-click copy)
- Regenerate button (retry with same query)

### State 4: Error State

**Visual**:
- Error message (red text, clear explanation)
- Retry button
- Suggested action (e.g., "Try switching provider")

**Behavior**:
- If provider fails → automatic fallback (transparent)
- If all providers fail → show error message
- User can retry or switch provider manually

### State 5: Artifact Rendered

**Visual**:
- Response text with artifact code block
- Rendered artifact in sandboxed iframe
- Toolbar: Copy code, Download, Open in new tab

**Behavior**:
- Click "Copy" → copies HTML/Markdown to clipboard
- Click "Download" → downloads as file
- Click "Open in new tab" → opens artifact in new browser tab

---

## 4. Responsive Behavior

### Desktop (≥1024px)

**Layout**:
- Sidebar: fixed width (280px)
- Main area: flexible width (calc(100% - 280px))
- Chat history: max-width 800px, centered

**Behavior**:
- Sidebar always visible
- Session list scrollable
- Starter cards in 2x2 grid

### Tablet (768px - 1023px)

**Layout**:
- Sidebar: collapsible (hamburger menu)
- Main area: full width
- Chat history: max-width 700px, centered

**Behavior**:
- Sidebar hidden by default
- Click hamburger → sidebar slides in
- Click outside sidebar → closes
- Starter cards in 2x2 grid

### Mobile (<768px)

**Layout**:
- Sidebar: full-screen overlay
- Main area: full width
- Chat history: full width (no max-width)

**Behavior**:
- Sidebar hidden by default
- Click hamburger → sidebar overlays main area
- Starter cards in single column
- Input area fixed to bottom
- Swipe right → open sidebar
- Swipe left → close sidebar

### Breakpoints

```css
/* Mobile first */
@media (min-width: 768px) {
  /* Tablet */
  .sidebar { width: 280px; }
}

@media (min-width: 1024px) {
  /* Desktop */
  .sidebar { width: 280px; }
  .main { margin-left: 280px; }
}
```

---

## 5. Accessibility Considerations

### WCAG 2.1 AA Compliance

**Color Contrast**:
- Text: #e2e8f0 on #0a0d14 (contrast ratio: 15.2:1) ✅
- Muted text: #94a3b8 on #0a0d14 (contrast ratio: 7.8:1) ✅
- Accent: #6366f1 on #0a0d14 (contrast ratio: 4.6:1) ✅

**Keyboard Navigation**:
- Tab order: New Chat → Session List → Chat History → Input → Send
- All interactive elements focusable
- Focus indicator: 2px solid outline (accent color)
- Keyboard shortcuts:
  - ⌘K / Ctrl+K → New chat
  - Enter → Send message
  - Shift+Enter → New line
  - Escape → Close sidebar (mobile)

**Screen Reader Support**:
- ARIA labels on all interactive elements
- Semantic HTML (nav, main, section, article)
- Live regions for streaming responses
- Announce: "Assistant is typing..." during streaming

**Focus Management**:
- Focus moves to input after new chat
- Focus returns to trigger after modal closes
- Focus trap in modals (prevent tabbing outside)

### Accessibility Features

1. **Skip to Main Content**
   - Hidden link at top of page
   - Keyboard users can skip sidebar navigation

2. **Reduced Motion**
   - Respect `prefers-reduced-motion` media query
   - Disable animations if user prefers reduced motion

3. **High Contrast Mode**
   - Detect `prefers-contrast: more`
   - Increase contrast ratios for text and borders

4. **Font Size**
   - Base font size: 16px (accessible default)
   - Use `rem` units (respects user's browser settings)
   - Allow zoom up to 200% without breaking layout

---

## 6. Design Decisions

### Decision 1: Dark Mode Only

**Choice**: Dark mode by default, no light mode toggle

**Rationale**:
- Reduces eye strain for long sessions (PMs use during work hours)
- Modern, professional aesthetic (matches ChatGPT, Claude, Linear)
- Simpler implementation (no theme switching logic)
- Consistent brand identity

**Trade-off**: Users who prefer light mode can't switch
**Mitigation**: Use classic dark palette (not neon purple) to reduce eye strain

### Decision 2: Official Brand Logos

**Choice**: Use official OpenAI, Anthropic, Ollama, OpenRouter SVGs

**Rationale**:
- Builds trust (users recognize brands)
- Professional appearance (not generic icons)
- Clear provider identification

**Trade-off**: Requires maintaining SVG library
**Mitigation**: Centralized in `ProviderLogos.tsx` component

### Decision 3: Minimalist Monogram

**Choice**: Replace purple "L" square with path-based "L" monogram

**Rationale**:
- Cleaner, more professional
- Consistent with brand logo aesthetic
- Scales better at different sizes

**Trade-off**: Less distinctive than colorful square
**Mitigation**: Use monogram consistently across app (logo, avatar, streaming indicator)

### Decision 4: No Header Bar

**Choice**: Remove top "New Chat" header bar

**Rationale**:
- Cleaner canvas (more space for content)
- Redundant with sidebar "New Chat" button
- Matches ChatGPT/Claude aesthetic

**Trade-off**: Less prominent "New Chat" action
**Mitigation**: Sidebar button always visible, keyboard shortcut (⌘K)

### Decision 5: Understated New Chat Button

**Choice**: Dark background with subtle border (not gradient purple)

**Rationale**:
- Professional, classic appearance
- Doesn't compete with content
- Matches overall design system

**Trade-off**: Less prominent than gradient button
**Mitigation**: Always visible in sidebar, keyboard shortcut (⌘K)

### Decision 6: Starter Cards

**Choice**: 3-4 example queries on welcome screen

**Rationale**:
- Helps new users understand capabilities
- Reduces blank canvas anxiety
- Encourages exploration

**Trade-off**: Takes up space on welcome screen
**Mitigation**: Understated design (muted colors, small text)

### Decision 7: Citation Placement

**Choice**: Citations below assistant messages (not inline)

**Rationale**:
- Keeps response text clean and readable
- Easy to scan sources
- Matches academic citation style

**Trade-off**: Citations separated from relevant text
**Mitigation**: Use [Source N] notation in response, matching citation list

### Decision 8: Sandboxed Artifacts

**Choice**: Render artifacts in `<iframe sandbox="...">`

**Rationale**:
- Prevents XSS attacks
- Isolates artifact from main app
- Safe for user-generated content

**Trade-off**: Artifacts can't access main app state
**Mitigation**: Artifacts are self-contained (no external dependencies)

### Decision 9: Streaming Responses

**Choice**: Stream tokens as they generate (SSE)

**Rationale**:
- Better UX (see progress, not stuck waiting)
- Reduces perceived latency
- Matches ChatGPT/Claude experience

**Trade-off**: More complex implementation (SSE)
**Mitigation**: FastAPI supports SSE natively, React handles streaming

### Decision 10: Session List Limit

**Choice**: Show last 20 sessions in sidebar

**Rationale**:
- Prevents sidebar from becoming overwhelming
- Most users don't need more than 20 recent sessions
- Performance (loading 20 sessions is fast)

**Trade-off**: Older sessions not visible
**Mitigation**: Search functionality (future enhancement)

---

## 7. Color Palette

### Surface Colors

```css
--surface-0: #0a0d14;  /* Background (deepest) */
--surface-1: #111622;  /* Sidebar, cards */
--surface-2: #1a1f2e;  /* Input area, buttons */
--surface-3: #252b3b;  /* Hover states, borders */
```

### Text Colors

```css
--text-primary: #e2e8f0;    /* Main text */
--text-secondary: #94a3b8;  /* Muted text */
--text-tertiary: #64748b;   /* Disabled text */
```

### Accent Colors

```css
--accent-primary: #6366f1;   /* Indigo (links, buttons) */
--accent-secondary: #8b5cf6; /* Purple (hover states) */
--accent-success: #10b981;   /* Green (success) */
--accent-error: #ef4444;     /* Red (errors) */
```

### Brand Colors

```css
--openai: #10A37F;      /* OpenAI green */
--anthropic: #D4A574;   /* Anthropic tan */
--ollama: #000000;      /* Ollama black */
--openrouter: #6366f1;  /* OpenRouter indigo */
```

---

## 8. Typography

### Font Family

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
```

**Rationale**: System fonts for fast loading, native feel

### Font Sizes

```css
--text-xs: 0.75rem;   /* 12px (labels, badges) */
--text-sm: 0.875rem;  /* 14px (secondary text) */
--text-base: 1rem;    /* 16px (body text) */
--text-lg: 1.125rem;  /* 18px (headings) */
--text-xl: 1.25rem;   /* 20px (large headings) */
--text-2xl: 1.5rem;   /* 24px (page titles) */
```

### Line Heights

```css
--leading-tight: 1.25;   /* Headings */
--leading-normal: 1.5;   /* Body text */
--leading-relaxed: 1.75; /* Long-form content */
```

---

## 9. Spacing System

```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-12: 3rem;    /* 48px */
```

**Usage**:
- Padding: `--space-4` (16px) for cards, `--space-6` (24px) for sections
- Margin: `--space-4` (16px) between elements, `--space-8` (32px) between sections
- Gap: `--space-2` (8px) for tight spacing, `--space-4` (16px) for loose spacing

---

## 10. Component Library

### Buttons

**Primary Button**:
```css
.bg-accent-primary.hover:bg-accent-secondary.text-white.px-4.py-2.rounded-md
```

**Secondary Button**:
```css
.bg-surface-2.hover:bg-surface-3.border.border-white/10.text-slate-300.px-4.py-2.rounded-md
```

**Icon Button**:
```css
.bg-transparent.hover:bg-surface-2.text-slate-400.hover:text-white.p-2.rounded-md
```

### Cards

**Session Card**:
```css
.bg-surface-1.hover:bg-surface-2.border.border-white/5.px-4.py-3.rounded-md.cursor-pointer
```

**Starter Card**:
```css
.bg-surface-1/60.border.border-white/5.px-4.py-3.rounded-md.cursor-pointer
```

### Input

**Text Input**:
```css
.bg-surface-2.border.border-white/10.focus:border-accent-primary.text-white.px-4.py-2.rounded-md
```

**Textarea**:
```css
.bg-surface-2.border.border-white/10.focus:border-accent-primary.text-white.px-4.py-2.resize-none
```

### Citations

**Citation Card**:
```css
.bg-surface-1.border.border-white/5.px-3.py-2.rounded-md.text-sm
```

---

## 11. Animation Guidelines

### Duration

```css
--duration-fast: 150ms;    /* Hover states, toggles */
--duration-normal: 250ms;  /* Modals, dropdowns */
--duration-slow: 400ms;    /* Page transitions */
```

### Easing

```css
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);  /* Default */
--ease-in: cubic-bezier(0.4, 0, 1, 1);        /* Exiting */
--ease-out: cubic-bezier(0, 0, 0.2, 1);       /* Entering */
```

### Usage

- **Hover states**: `--duration-fast` + `--ease-in-out`
- **Modals**: `--duration-normal` + `--ease-out` (enter), `--ease-in` (exit)
- **Page transitions**: `--duration-slow` + `--ease-in-out`

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 12. Conclusion

The Lenny Growth Assistant design system prioritizes:

1. **Clarity**: Clean, minimalist interface with no clutter
2. **Professionalism**: Classic dark palette, official brand logos
3. **Accessibility**: WCAG 2.1 AA compliant, keyboard navigation
4. **Responsiveness**: Mobile-first, works on all screen sizes
5. **Performance**: Streaming responses, fast loading states

**Design Principles**:
- Content is the hero, not the chrome
- Progressive disclosure (show what's needed, when)
- Understated elegance (not loud neon)
- Accessibility first (keyboard, screen reader, contrast)

**Next Steps**:
- Implement component library in Tailwind
- Create Storybook for component documentation
- Conduct usability testing with 5 PMs
- Iterate based on feedback

---

**Repository**: https://github.com/Sudesh-chandra/lenny-growth-assistant
**Figma**: (link to design files if available)
**Storybook**: (link to component library if available)
