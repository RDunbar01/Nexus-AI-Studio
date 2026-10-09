# Appearance

Settings → General AI → Comfort & appearance includes panel opacity (75–100%), background artwork opacity (0–100%) and glass blur (0–26 px). Defaults are 94%, 50% and 16 px. Reset transparency changes only these three preferences.

Text opacity is never changed. Solid panels and high contrast override glass panel backgrounds; reduce-motion and operating-system reduced-effects preferences disable blur. Existing text size, theme, workspace depth and accessibility controls remain available. Values persist through the established local settings transaction and export/import schema. Malformed imports fail before applying other fields. Invalid saved values fall back to defaults.

The controls were tested with Node/jsdom for persistence, validation, reset, lock, interrupted/repeated changes and no duplicated controls. Actual browser visual rendering and device-specific contrast have not been measured.
