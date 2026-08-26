/**
 * Provider Logo SVG Components
 * Simplified, recognizable brand marks for each LLM provider.
 */

export function OpenAILogo({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L2 7l10 5 10-5-10-5z" fill="#10A37F" opacity="0.9"/>
      <path d="M2 17l10 5 10-5" stroke="#10A37F" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M2 12l10 5 10-5" stroke="#10A37F" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

export function AnthropicLogo({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" fill="#D4A574" opacity="0.15"/>
      <path d="M8 18l4-12 4 12" stroke="#D4A574" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      <path d="M9.5 14h5" stroke="#D4A574" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  );
}

export function OllamaLogo({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="3" width="18" height="18" rx="4" fill="#1a1a2e" stroke="#6366f1" strokeWidth="1.5"/>
      <circle cx="9" cy="10" r="1.5" fill="#6366f1"/>
      <circle cx="15" cy="10" r="1.5" fill="#6366f1"/>
      <path d="M9 15c0 0 1.5 2 3 2s3-2 3-2" stroke="#6366f1" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  );
}

export function OpenRouterLogo({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L4 7v10l8 5 8-5V7l-8-5z" stroke="#6366f1" strokeWidth="1.5" fill="none"/>
      <path d="M12 2v20M4 7l8 5 8-5M4 17l8-5 8 5" stroke="#6366f1" strokeWidth="1" opacity="0.5"/>
      <circle cx="12" cy="12" r="3" fill="#6366f1" opacity="0.3"/>
      <circle cx="12" cy="12" r="1.5" fill="#6366f1"/>
    </svg>
  );
}

/**
 * Brand mark for the Lenny Growth Assistant app.
 * Replaces the rocket emoji with a polished gradient logo.
 */
export function LennyBrandLogo({ size = 36 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="lenny-grad" x1="0" y1="0" x2="36" y2="36" gradientUnits="userSpaceOnUse">
          <stop stopColor="#6366f1"/>
          <stop offset="1" stopColor="#8b5cf6"/>
        </linearGradient>
      </defs>
      <rect x="2" y="2" width="32" height="32" rx="8" fill="url(#lenny-grad)"/>
      <text x="18" y="24" textAnchor="middle" fill="white" fontSize="18" fontWeight="700" fontFamily="Inter, system-ui, sans-serif">L</text>
    </svg>
  );
}

/**
 * Small assistant avatar — used in message bubbles and streaming indicator.
 */
export function LennyAvatar({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="av-grad" x1="0" y1="0" x2="28" y2="28" gradientUnits="userSpaceOnUse">
          <stop stopColor="#6366f1" stopOpacity="0.2"/>
          <stop offset="1" stopColor="#8b5cf6" stopOpacity="0.2"/>
        </linearGradient>
      </defs>
      <rect x="1" y="1" width="26" height="26" rx="7" fill="url(#av-grad)" stroke="#6366f1" strokeOpacity="0.2" strokeWidth="1"/>
      <path d="M14 7l2 4.5 5 .7-3.6 3.5.85 4.8L14 18.2l-4.25 2.3.85-4.8L7 12.2l5-.7L14 7z" fill="#6366f1" opacity="0.8"/>
    </svg>
  );
}

/**
 * Podcast source icon — replaces the microphone emoji in citation popovers.
 */
export function PodcastSourceIcon({ size = 14 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="7" cy="7" r="6" fill="#6366f1" opacity="0.15"/>
      <path d="M7 3v4l2.5 1.5" stroke="#6366f1" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
      <circle cx="7" cy="7" r="4" stroke="#6366f1" strokeWidth="0.8" opacity="0.4"/>
    </svg>
  );
}
