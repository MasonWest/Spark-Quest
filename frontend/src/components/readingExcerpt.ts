export function extractReading(text: string, startMarker: string, endMarker: string): string | null {
  const start = text.indexOf(startMarker);
  if (start < 0 || text.indexOf(startMarker, start + startMarker.length) >= 0) return null;
  const from = start + startMarker.length;
  const end = text.indexOf(endMarker, from);
  if (end < 0) return null;
  const excerpt = text.slice(from, end).trim();
  return excerpt || null;
}

