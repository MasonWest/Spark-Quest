export interface JourneyOption { id: string; text: string; feedback: string }
export interface AnswerField {
  id: string; label: string; options: JourneyOption[]; correctOptionId: string;
  input?: { kind: "integer" | "text"; acceptedAnswers: string[]; placeholder: string; incorrectOptionId: string };
}
export interface JourneyRemedy {
  id: string; knowledgeId: string; title: string; intro: string; code: string;
  prompt: string; field: AnswerField; insight: string;
}
export interface JourneyTask {
  id: string; knowledgeIds: string[]; title: string; intro: string; code: string;
  prompt: string; fields: AnswerField[]; insight: string; ability: string;
  table?: { caption?: string; columns: string[]; rows: (string | number)[][] };
  remediation?: JourneyRemedy;
  reading?: {
    id: string; title: string; sectionTitle?: string; startMarker: string; endMarker: string;
    connection: string; boundary: string; caution?: string;
  };
}
export interface JourneyLesson {
  slug: string; version: number; legacyTaskIds?: string[]; title: string; mission: string; correction: string;
  source: string; next: string; tasks: JourneyTask[];
  project?: { downloads: { label: string; href: string }[]; solution: { label: string; href: string }; solutionNote?: string; checksums?: Record<string, string> };
}
export interface JourneyMetadata {
  slug: string; version: number; title: string; tasks: { id: string }[]; legacyTaskIds?: string[];
}
import index from "./journeyIndex.json";
export const journeyIndex: Record<string, JourneyMetadata> = index;
const files = import.meta.glob<{ default: JourneyLesson }>("./lessons/*.json");
export async function loadJourney(slug: string): Promise<JourneyLesson | null> {
  const loader = files[`./lessons/${slug}.json`];
  return loader ? (await loader()).default : null;
}
