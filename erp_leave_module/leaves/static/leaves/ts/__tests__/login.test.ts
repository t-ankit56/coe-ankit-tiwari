import { afterEach, describe, expect, it, vi } from "vitest";
import { navigation } from "../api.js";
import { submitLogin } from "../login.js";

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("successful login", () => {
  it("goes to My leaves without calling /api/me again", async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ id: 1, name: "Ankit Tiwari", email: "ankit@incubyte.co" }),
    });
    vi.stubGlobal("fetch", fetchSpy);
    const goTo = vi.spyOn(navigation, "goTo").mockImplementation(() => {});

    await submitLogin("ankit@incubyte.co", "password123");

    expect(goTo).toHaveBeenCalledWith("/");
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(fetchSpy.mock.calls[0][0]).toBe("/api/login");
  });
});
