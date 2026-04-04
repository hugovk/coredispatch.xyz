import type { IssueCredit } from "@/lib/types";

interface CreditsProps {
  credits: IssueCredit[];
}

export function Credits({ credits }: CreditsProps) {
  return (
    <div className="mt-10 border-t border-border pt-6 text-center text-sm text-muted">
      <p className="font-medium text-foreground/60">This edition brought to you by:</p>
      <p className="mt-2">
        {credits.map((credit, i) => (
          <span key={credit.name}>
            {i > 0 && ", "}
            {credit.url ? (
              <a href={credit.url} className="text-accent hover:text-accent-hover transition-colors">
                {credit.name}
              </a>
            ) : (
              credit.name
            )}
          </span>
        ))}
      </p>
    </div>
  );
}
