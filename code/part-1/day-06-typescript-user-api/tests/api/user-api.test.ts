import { describe, expect, it } from "vitest";
import { fetchUser } from "../../src/api/user-api.js";
import { fakeFetch } from "../support/fake-fetch.js";
import { validUser } from "../support/fixtures.js";

describe("fetchUser", () => {
  it("returns the user when the response is a valid user", async () => {
    const user = await fetchUser(1, fakeFetch(validUser));

    expect(user).toEqual(validUser);
  });

  it("requests the JSONPlaceholder URL for the given id", async () => {
    const fetchFn = fakeFetch(validUser);

    await fetchUser(7, fetchFn);

    expect(fetchFn.urls).toEqual(["https://jsonplaceholder.typicode.com/users/7"]);
  });

  it("rejects when the response is missing the email field", async () => {
    const { email: _email, ...withoutEmail } = validUser;

    await expect(fetchUser(1, fakeFetch(withoutEmail))).rejects.toThrow(
      "Response is not a valid user",
    );
  });
});
