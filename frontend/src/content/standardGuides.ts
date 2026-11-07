import data from "./standardGuides.json";
export interface StandardSection { id: string; title: string; body: string; boundary: string }
export interface StandardGuide { title: string; sections: StandardSection[]; sources: {title: string; url: string}[] }
export const standardGuides: Record<string, StandardGuide> = data.lessons;
