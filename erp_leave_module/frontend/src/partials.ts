// A page can pull in a shared piece of HTML with a comment such as
// <!-- include: partials/sidebar.html -->. Plain HTML has no include, so this replaces the
// comment with the file's contents. The Vite dev server and the tests both use it.
const INCLUDE_COMMENT = /<!--\s*include:\s*(\S+?)\s*-->/g;

export function inlinePartials(html: string, readPartial: (path: string) => string): string {
  return html.replace(INCLUDE_COMMENT, (_comment, path: string) => readPartial(path));
}
