import type { AnswerField } from "../content/journeys";

export function normalizeResponse(raw: string, kind: "integer" | "text"): string | null {
  const value = raw.normalize("NFKC").trim();
  if (!value) return null;
  if (kind === "integer") {
    if (!/^[+-]?\d+$/.test(value) || !Number.isSafeInteger(Number(value))) return null;
    return String(Number(value));
  }
  return value.replace(/、/g, ",").replace(/\s*([,=\[\]\(\)])\s*/g, "$1").replace(/\s+/g, " ");
}

// Store a canonical option identity so existing versioned evidence stays usable.
// The raw response is retained separately in the attempt for later inspection.
export function responseOption(field: AnswerField, raw: string): string | undefined {
  if (!field.input || !raw.trim()) return undefined;
  const value = normalizeResponse(raw, field.input.kind);
  return value !== null && field.input.acceptedAnswers.some(answer => normalizeResponse(answer, field.input!.kind) === value)
    ? field.correctOptionId : field.input.incorrectOptionId;
}
