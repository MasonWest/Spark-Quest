export interface JourneyOption { id: string; text: string; feedback: string }
export interface AnswerField { id: string; label: string; options: JourneyOption[]; correctOptionId: string }
export interface JourneyTask {
  id: string; knowledgeIds: string[]; title: string; intro: string; code: string;
  prompt: string; fields: AnswerField[]; insight: string; ability: string;
  table?: { caption?: string; columns: string[]; rows: (string | number)[][] };
  reading?: {
    id: string; title: string; sectionTitle?: string; startMarker: string; endMarker: string;
    connection: string; boundary: string;
  };
}
export interface JourneyLesson {
  slug: string; version: number; legacyTaskIds?: string[]; title: string; mission: string; correction: string;
  source: string; next: string; tasks: JourneyTask[];
  project?: { downloads: { label: string; href: string }[]; solution: { label: string; href: string } };
}
const files = import.meta.glob<{ default: JourneyLesson }>("./lessons/*.json", { eager: true });
export const journeys: Record<string, JourneyLesson> = Object.fromEntries(
  Object.values(files).map(file => [file.default.slug, file.default])
);
