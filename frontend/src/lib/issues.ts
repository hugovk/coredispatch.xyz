import fs from "node:fs";
import path from "node:path";
import YAML from "yaml";
import type { Issue } from "./types";

const EDITIONS_DIR = process.env.EDITIONS_DIR || path.join(process.cwd(), "..", "editions");
const DRAFTS_DIR = process.env.DRAFTS_DIR || path.join(process.cwd(), "..", "drafts");

function loadFromDir(dir: string): Issue[] {
  if (!fs.existsSync(dir)) return [];

  const files = fs
    .readdirSync(dir)
    .filter((f: string) => f.endsWith(".yml") && !f.startsWith("_") && !f.startsWith("."));

  const issues: Issue[] = [];

  for (const f of files) {
    try {
      const data = YAML.parse(fs.readFileSync(path.join(dir, f), "utf-8"));
      if (!data?.number) continue;
      issues.push({
        ...data,
        period_start: data.period_start || data.week_start || "",
        period_end: data.period_end || data.week_end || "",
        items: data.items || [],
      } as Issue);
    } catch {
      continue;
    }
  }

  return issues.sort((a: Issue, b: Issue) => b.number - a.number);
}

export function getAllEditions(): Issue[] {
  return loadFromDir(EDITIONS_DIR);
}

export function getEdition(num: number): Issue | undefined {
  return getAllEditions().find((i) => i.number === num);
}

export function getAdjacentEditions(num: number) {
  const all = getAllEditions();
  const idx = all.findIndex((i) => i.number === num);
  return {
    prev: idx < all.length - 1 ? all[idx + 1] : null,
    next: idx > 0 ? all[idx - 1] : null,
  };
}

export function getAllDrafts(): Issue[] {
  return loadFromDir(DRAFTS_DIR);
}

export function getDraft(num: number): Issue | undefined {
  return getAllDrafts().find((i) => i.number === num);
}
