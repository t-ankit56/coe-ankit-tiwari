import { describe, expect, it } from "vitest";
import { inlinePartials } from "../partials.js";

describe("including a partial", () => {
  it("replaces the include comment with the contents of the partial file", () => {
    const page = '<body><!-- include: partials/sidebar.html --><main id="main"></main></body>';
    const readPartial = (path: string) => (path === "partials/sidebar.html" ? "<aside>Sidebar</aside>" : "");

    expect(inlinePartials(page, readPartial)).toBe('<body><aside>Sidebar</aside><main id="main"></main></body>');
  });
});
