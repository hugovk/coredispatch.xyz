import type { Item, Section } from "@/lib/types";
import { SECTION_LABELS, SECTION_DESCRIPTIONS } from "@/lib/types";
import { ItemCard } from "./ItemCard";

const SECTION_ICONS: Record<Section, string> = {
  upcoming_releases: "\u{1F4E6}",
  official_news: "\u{1F4E2}",
  pep_updates: "\u{1F4DC}",
  steering_council: "\u{1F3DB}\u{FE0F}",
  merged_prs: "\u{1F40D}",
  discussions: "\u{1F4AC}",
  events: "\u{1F4C5}",
  musings: "\u{270D}\u{FE0F}",
  picks: "\u{2B50}",
};

// Sections that render as a compact grid
const COMPACT_SECTIONS: Set<Section> = new Set(["events"]);

interface SectionBlockProps {
  section: Section;
  items: Item[];
}

export function SectionBlock({ section, items }: SectionBlockProps) {
  if (items.length === 0) return null;

  const isCompact = COMPACT_SECTIONS.has(section);

  const description = SECTION_DESCRIPTIONS[section];

  return (
    <section className="mb-10">
      <div className="mb-2 pb-2 border-b border-border">
        <div className="flex items-center gap-2.5">
          <span className="text-lg">{SECTION_ICONS[section]}</span>
          <h2 className="text-base font-semibold">{SECTION_LABELS[section]}</h2>
          <span className="rounded-full bg-accent-light px-2 py-0.5 text-xs font-medium text-accent">
            {items.length}
          </span>
        </div>
        {description && (
          <p className="mt-1 text-xs text-muted">{description}</p>
        )}
      </div>
      {section === "upcoming_releases" ? (
        <div className="flex flex-wrap gap-2 mt-1">
          {items.map((item) => (
            <a
              key={item.id}
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-lg border border-border bg-surface px-3.5 py-2 text-sm font-medium hover:border-accent/40 hover:shadow-sm transition-all"
            >
              <span>{item.title}</span>
              <span className="text-xs text-muted">{item.summary}</span>
            </a>
          ))}
        </div>
      ) : isCompact ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6">
          {items.map((item) => (
            <ItemCard key={item.id} item={item} compact />
          ))}
        </div>
      ) : (
        <div className="divide-y divide-border/40">
          {items.map((item) => (
            <ItemCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </section>
  );
}
