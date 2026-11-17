import { describe, expect, it } from "vitest";
import { fetchUser } from "../../src/api/user-api.js";
import { fakeFetch } from "../support/fake-fetch.js";
import { validUser } from "../support/fixtures.js";

describe("fetchUser", () => {
  it("returns the user when the response is a valid user", async () => {
    const user = await fetchUser(1, fakeFetch(validUser));

    expect(user).toEqual(validUser);
  });
});
