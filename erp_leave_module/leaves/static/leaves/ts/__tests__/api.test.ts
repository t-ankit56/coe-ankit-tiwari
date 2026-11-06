import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, apiGet, apiPost, navigation } from "../api.js";

function answerWith(status: number, body: unknown) {
  const fetchSpy = vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  });
  vi.stubGlobal("fetch", fetchSpy);
  return fetchSpy;
}

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("post", () => {
  it("sends the CSRF token from the cookie in the X-CSRFToken header", async () => {
    document.cookie = "csrftoken=abc";
    const fetchSpy = answerWith(200, {});

    await apiPost("/api/leaves", { reason: "Trip" });

    const [, options] = fetchSpy.mock.calls[0];
    expect(options.method).toBe("POST");
    expect(options.headers["X-CSRFToken"]).toBe("abc");
    expect(options.body).toBe(JSON.stringify({ reason: "Trip" }));
  });
});

describe("any call", () => {
  it("redirects to the login page when the server answers 401", async () => {
    answerWith(401, { error: "Authentication credentials were not provided." });
    const goTo = vi.spyOn(navigation, "goTo").mockImplementation(() => {});

    await expect(apiGet("/api/me")).rejects.toBeInstanceOf(ApiError);

    expect(goTo).toHaveBeenCalledWith("/login");
  });
});
