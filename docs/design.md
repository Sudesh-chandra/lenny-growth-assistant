# Design Document
## The Lenny Growth Assistant — UI/UX

---

## 1. Design Principles

1. **Clarity over cleverness**: Every element should have a clear purpose. No decorative UI that doesn't serve the user.
2. **Progressive disclosure**: Show the chat first, reveal artifacts and citations on demand.
3. **Responsive feedback**: Streaming tokens, loading states, and error messages keep the user informed.
4. **Accessibility**: Keyboard navigable, sufficient color contrast, semantic HTML, ARIA labels where needed.
5. **Trust through transparency**: Citations, source attribution, and "I don't know" responses build user trust.

## 2. Information Architecture

```
┌─────────────────────────────────────────────────────┐
│ App Shell                                            │
├──────────┬──────────────────────────┬───────────────┤
│ Sidebar  │ Chat View               │ Artifact      │
│ (280px)  │ (flex-1)                │ Viewer (50%)  │
│          │                         │ (conditional) │
│ ┌──────┐ │ ┌─────────────────────┐ │ ┌───────────┐ │
│ │ Logo │ │ │ Header (title)      │ │ │ Tabs:     │ │
│ ├──────┤ │ ├─────────────────────┤ │ │ Preview   │ │
│ │ New  │ │ │ Messages area       │ │ │ Code      │ │
│ │ Chat │ │ │                     │ │ ├───────────┤ │
│ ├──────┤ │ │ • User bubbles      │ │ │ Content   │ │
│ │ Model│ │ │ • Assistant bubbles │ │ │ (iframe/  │ │
│ │ Sel. │ │ │ • Streaming cursor  │ │ │  markdown)│ │
│ ├──────┤ │ │ • Loading indicator │ │ └───────────┘ │
│ │ Sess-│ │ ├─────────────────────┤ │               │
│ │ ions │ │ │ Input area          │ │               │
│ │ List │ │ │ (textarea + send)   │ │               │
│ └──────┘ │ └─────────────────────┘ │               │
└──────────┴──────────────────────────┴───────────────┘
```

## 3. Key Interaction States

### 3.1 Empty State (Welcome Screen)
- Large app logo and name
- Brief description of capabilities
- 4 suggestion cards for quick-start queries
- Clean, inviting design

### 3.2 Streaming Response
- Token-by-token text appearance
- Animated cursor at the end of streaming text
- Citations appear above the streaming text as they're resolved
- "Thinking..." spinner shown before first token

### 3.3 Error State
- Toast notification (top-right) with error message
- Dismissible with X button
- Auto-dismiss after 10 seconds
- Red color scheme for visibility

### 3.4 Artifact Panel
- Slides in from the right with animation
- Dual-tab interface: Preview | Code
- Copy button with check-mark confirmation
- Close button to collapse panel

### 3.5 Model Switching
- Toggle buttons for provider (Local / OpenAI / Claude)
- Dropdown for specific model selection
- Status indicator (green = available, gray = offline)
- Visual feedback on selection change

## 4. Responsive Behavior

| Breakpoint | Sidebar | Chat | Artifact |
|-----------|---------|------|----------|
| >1200px | Fixed 280px | flex-1 | 50% when open |
| 768-1200px | Collapsible (toggle) | Full width | Overlay (80%) |
| <768px | Hidden (drawer) | Full width | Full-screen overlay |

## 5. Color System

| Token | Value | Usage |
|-------|-------|-------|
| `primary-600` | `#0284c7` | Buttons, user bubbles, active states |
| `primary-100` | `#e0f2fe` | Assistant avatar, citation badges |
| `slate-900` | `#0f172a` | Sidebar background |
| `slate-50` | `#f8fafc` | App background |
| `white` | `#ffffff` | Message bubbles, cards |
| `red-50/200/700` | Error states | Error toasts |
| `green-400` | Status indicator | Ollama available |

## 6. Typography

- **Font family**: System font stack (-apple-system, BlinkMacSystemFont, Segoe UI, Roboto)
- **Headings**: Bold (700), tight tracking
- **Body**: Regular (400), 1.7 line-height for readability
- **Code**: Monospace, dark background, syntax highlighting
- **Citations**: Small (0.75rem), pill-shaped badges

## 7. Accessibility Considerations

- All interactive elements are keyboard-accessible
- Focus states visible with ring indicators
- Color contrast ratios meet WCAG AA (4.5:1 for text)
- ARIA labels on icon-only buttons
- Screen reader-friendly message structure
- Reduced motion support for animations
- Text can be resized up to 200% without breaking layout

## 8. Design Decisions & Trade-offs

### Why dual-pane instead of modal for artifacts?
Side-by-side viewing lets users reference the conversation while examining the artifact. Modals would hide context.

### Why SSE streaming instead of WebSocket?
SSE is simpler, unidirectional (server→client), and works with standard HTTP infrastructure. The chat only needs server-to-client streaming.

### Why system font stack?
Performance (no font loading), native feel on each OS, and sufficient quality for a productivity tool.

### Why collapsible sidebar?
Maximizes chat space on smaller screens while keeping session history accessible.
