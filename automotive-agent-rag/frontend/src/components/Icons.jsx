// Hand-built monoline icon set (no emoji, no external icon library).
const base = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.75,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

function Svg({ children, className = "w-4 h-4", ...rest }) {
  return (
    <svg viewBox="0 0 24 24" className={className} {...base} {...rest}>
      {children}
    </svg>
  );
}

export const IconCar = (p) => (
  <Svg {...p}>
    <path d="M3 13.5 4.7 8.8A2 2 0 0 1 6.6 7.5h10.8a2 2 0 0 1 1.9 1.3l1.7 4.7" />
    <path d="M3 13.5h18v4a1 1 0 0 1-1 1h-1.5a1 1 0 0 1-1-1V16h-11v1.5a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z" />
    <circle cx="7" cy="17" r="1.4" />
    <circle cx="17" cy="17" r="1.4" />
  </Svg>
);

export const IconGauge = (p) => (
  <Svg {...p}>
    <path d="M4 15a8 8 0 1 1 16 0" />
    <path d="M12 15 15.2 9.8" />
    <path d="M4 15h1.2M18.8 15H20" />
  </Svg>
);

export const IconBell = (p) => (
  <Svg {...p}>
    <path d="M6 10a6 6 0 1 1 12 0c0 3.2 1 4.6 1.6 5.4H4.4C5 14.6 6 13.2 6 10Z" />
    <path d="M10 18.5a2 2 0 0 0 4 0" />
  </Svg>
);

export const IconSnow = (p) => (
  <Svg {...p}>
    <path d="M12 3v18M4.5 7.5l15 9M4.5 16.5l15-9" />
    <path d="M12 3l-1.6 1.6M12 3l1.6 1.6M12 21l-1.6-1.6M12 21l1.6-1.6" />
  </Svg>
);

export const IconFlame = (p) => (
  <Svg {...p}>
    <path d="M12 21c4 0 6.5-2.6 6.5-6 0-3-2-4.7-3-7-1 1.6-1.8 2-2.6 1-1-1.3-.5-3.4-.9-5-2.5 2-4 5.4-4 8.4 0 1 .3 1.9.8 2.7-.9-.3-1.6-1-2-1.9-.6 1-.8 2.1-.8 3 0 2.9 2 5.8 6 5.8Z" />
  </Svg>
);

export const IconUpload = (p) => (
  <Svg {...p}>
    <path d="M12 15V4M8 8l4-4 4 4" />
    <path d="M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" />
  </Svg>
);

export const IconTrash = (p) => (
  <Svg {...p}>
    <path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2M18 7l-.8 12a2 2 0 0 1-2 1.9H8.8a2 2 0 0 1-2-1.9L6 7" />
    <path d="M10 11v6M14 11v6" />
  </Svg>
);

export const IconSearch = (p) => (
  <Svg {...p}>
    <circle cx="10.5" cy="10.5" r="6.5" />
    <path d="M20 20l-4.8-4.8" />
  </Svg>
);

export const IconFile = (p) => (
  <Svg {...p}>
    <path d="M7 3h7l4 4v14a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z" />
    <path d="M14 3v4h4" />
    <path d="M9 13h6M9 17h6" />
  </Svg>
);

export const IconCheck = (p) => (
  <Svg {...p}>
    <path d="M5 13l4 4L19 7" />
  </Svg>
);

export const IconX = (p) => (
  <Svg {...p}>
    <path d="M6 6l12 12M18 6 6 18" />
  </Svg>
);

export const IconAlert = (p) => (
  <Svg {...p}>
    <path d="M12 3 2 20h20L12 3Z" />
    <path d="M12 10v4M12 17h.01" />
  </Svg>
);

export const IconRefresh = (p) => (
  <Svg {...p}>
    <path d="M4 4v5h5" />
    <path d="M20 20v-5h-5" />
    <path d="M5.5 15A7.5 7.5 0 0 0 19 12M18.5 9A7.5 7.5 0 0 0 5 12" />
  </Svg>
);

export const IconBolt = (p) => (
  <Svg {...p}>
    <path d="M13 3 5 13.5h5.5L11 21l8-11h-5.5L13 3Z" />
  </Svg>
);

export const IconBook = (p) => (
  <Svg {...p}>
    <path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H12v16H5.5A1.5 1.5 0 0 1 4 18.5v-13Z" />
    <path d="M20 5.5A1.5 1.5 0 0 0 18.5 4H12v16h6.5a1.5 1.5 0 0 0 1.5-1.5v-13Z" />
  </Svg>
);

export const IconBroom = (p) => (
  <Svg {...p}>
    <path d="M19 5 9 15" />
    <path d="M9 15c-1.8-1.8-4.8-1.8-6.5 0S1 20 2 21c1 1 4.2.5 6-1.3s1.8-4.7 1-4.7Z" />
    <path d="M14 3l7 7" />
  </Svg>
);

export const IconSun = (p) => (
  <Svg {...p}>
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2v2.5M12 19.5V22M4.2 4.2l1.8 1.8M18 18l1.8 1.8M2 12h2.5M19.5 12H22M4.2 19.8 6 18M18 6l1.8-1.8" />
  </Svg>
);

export const IconMoon = (p) => (
  <Svg {...p}>
    <path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5Z" />
  </Svg>
);

export const IconDatabase = (p) => (
  <Svg {...p}>
    <ellipse cx="12" cy="6" rx="7" ry="3" />
    <path d="M5 6v12c0 1.7 3.1 3 7 3s7-1.3 7-3V6" />
    <path d="M5 12c0 1.7 3.1 3 7 3s7-1.3 7-3" />
  </Svg>
);

export const IconCopy = (p) => (
  <Svg {...p}>
    <rect x="9" y="9" width="11" height="11" rx="1.5" />
    <path d="M6 15H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h9a1 1 0 0 1 1 1v1" />
  </Svg>
);

export const IconSend = (p) => (
  <Svg {...p}>
    <path d="M4 12 19.5 4 14 19l-2.8-6.2L4 12Z" />
  </Svg>
);

export const IconChevronRight = (p) => (
  <Svg {...p}>
    <path d="M9 6l6 6-6 6" />
  </Svg>
);

export const IconClock = (p) => (
  <Svg {...p}>
    <circle cx="12" cy="12" r="8.5" />
    <path d="M12 7.5V12l3 2" />
  </Svg>
);

export const IconLogout = (p) => (
  <Svg {...p}>
    <path d="M9 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h3" />
    <path d="M16 15l4-3-4-3" />
    <path d="M20 12H9" />
  </Svg>
);

export const IconLayers = (p) => (
  <Svg {...p}>
    <path d="m12 3 8.5 4.5L12 12 3.5 7.5 12 3Z" />
    <path d="m3.5 12 8.5 4.5L20.5 12" />
    <path d="m3.5 16.5 8.5 4.5 8.5-4.5" />
  </Svg>
);
