// Palette DressIT — marron / beige / doré, texte clair.
export const colors = {
  bg: "#17130e",
  bgAlt: "#1c1610",
  surface: "#241c15",
  surface2: "#2f251b",
  border: "#43331f",
  text: "#f9f5ee",
  textSoft: "#d6c6ac",
  textMuted: "#a3907a",
  gold: "#e0bd6a",
  goldDeep: "#b8912f",
  brown: "#55402f",
  brownDark: "#2f221a",
  fresh: "#2f9e83",
  white: "#ffffff",
  danger: "#c05b5b",
};

export const currency = "FCFA";

export function money(value) {
  const n = Math.round(Number(value) || 0);
  return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ") + " " + currency;
}
