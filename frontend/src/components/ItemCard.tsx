import type { Item } from "@/lib/types";

interface ItemCardProps {
  item: Item;
  compact?: boolean;
}

export function ItemCard({ item, compact }: ItemCardProps) {
  const meta = item.metadata_ as Record<string, unknown> | null;
  const section = item.section;

  // Compact mode — CFPs, conferences, news, musings
  if (compact) {
    return (
      <a
        href={item.url}
        target="_blank"
        rel="noopener noreferrer"
        className="group flex items-baseline justify-between gap-2 py-1.5 border-b border-border/30 last:border-0"
      >
        <span className="text-sm font-medium truncate group-hover:text-accent transition-colors">
          {item.title}
        </span>
        {item.summary && (
          <span className="shrink-0 text-xs text-muted">{item.summary}</span>
        )}
      </a>
    );
  }

  // Determine right-aligned detail
  let rightDetail: React.ReactNode = null;

  if (section === "pep_updates" && meta && "status" in meta) {
    const status = String(meta.status);
    const badgeColor = status === "Accepted" || status === "Final"
      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
      : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400";
    rightDetail = (
      <span className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${badgeColor}`}>
        {status}
      </span>
    );
  } else if (meta && "submitted_by" in meta) {
    rightDetail = (
      <span className="shrink-0 text-xs text-muted font-mono">
        via @{String(meta.submitted_by)}
      </span>
    );
  } else if (meta && "author" in meta) {
    const isHandle = String(meta.author).match(/^[a-zA-Z0-9_-]+$/);
    rightDetail = (
      <span className={`shrink-0 text-xs text-muted ${isHandle ? "font-mono" : ""}`}>
        {isHandle ? "@" : "by "}{String(meta.author)}
      </span>
    );
  } else if (item.summary) {
    rightDetail = (
      <span className="shrink-0 text-xs text-muted whitespace-nowrap">
        {item.summary}
      </span>
    );
  }

  return (
    <a
      href={item.url}
      target="_blank"
      rel="noopener noreferrer"
      className="group flex items-baseline justify-between gap-4 py-2.5"
    >
      <span className="text-[15px] font-medium group-hover:text-accent transition-colors">
        {item.title}
      </span>
      {rightDetail}
    </a>
  );
}
