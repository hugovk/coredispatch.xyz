/**
 * Simple markdown-to-HTML for editorial notes.
 * Handles: paragraphs, links, inline code, bold, italic.
 */
export function renderMarkdown(text: string): string {
  if (!text) return "";

  return text
    .split(/\n\n+/)
    .map((block) => {
      const html = block
        .trim()
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.+?)\*/g, "<em>$1</em>")
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
      return `<p>${html}</p>`;
    })
    .join("\n");
}
