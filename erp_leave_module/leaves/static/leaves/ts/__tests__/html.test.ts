import { describe, expect, it } from "vitest";
import { escapeHtml } from "../html.js";

describe("escapeHtml", () => {
  it("turns a <script> tag in user text into harmless text", () => {
    const escaped = escapeHtml("<script>alert('x')</script>");

    expect(escaped).not.toContain("<script>");
    expect(escaped).toContain("&lt;script&gt;");
    expect(escapeHtml(`Tom & "Jerry" it's`)).toBe("Tom &amp; &quot;Jerry&quot; it&#39;s");
  });
});
