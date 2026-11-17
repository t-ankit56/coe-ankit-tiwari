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

  it.each([
    ["id is missing", { ...validUser, id: undefined }],
    ["id is a string", { ...validUser, id: "1" }],
    ["name is a number", { ...validUser, name: 42 }],
    ["address is missing", { ...validUser, address: undefined }],
    ["address has no city", { ...validUser, address: {} }],
    ["address.city is a number", { ...validUser, address: { city: 5 } }],
    ["body is null", null],
    ["body is a string", "not a user"],
    ["body is an array", [validUser]],
  ])("rejects when %s", async (_label, body) => {
    await expect(fetchUser(1, fakeFetch(body))).rejects.toThrow(
      "Response is not a valid user",
    );
  });

  it("rejects with the status when the request is not ok", async () => {
    await expect(fetchUser(9999, fakeFetch({}, 404))).rejects.toThrow(
      "Request failed with status 404",
    );
  });
});
