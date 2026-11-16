import { expect, expectTypeOf, it } from "vitest";
import type { Notification } from "../src/models";
import { fail, type Result } from "../src/result";
import { makeService } from "./fakes";

it("a new service has sent nothing", () => {
  const { channels } = makeService();
  for (const channel of channels.values()) {
    expect(channel.sent).toEqual([]);
  }
});

it.each(["email", "sms"])("sending through %s reaches only that channel", (name) => {
  const { service, channels } = makeService();
  const notification = { to: "someone", body: "hi" };
  service.send(name, notification);
  for (const [channelName, channel] of channels) {
    expect(channel.sent).toEqual(channelName === name ? [notification] : []);
  }
});

it("a successful send returns ok with the notification as its value", () => {
  const { service } = makeService();
  const notification = { to: "a@x.com", body: "hi" };
  const result = service.send("email", notification);
  expect(result).toEqual({ ok: true, value: notification });
  if (result.ok) {
    expectTypeOf(result.value).toEqualTypeOf<Notification>();
  }
});

it("a failed result carries an error message and no value", () => {
  const result: Result<Notification> = fail("gateway down");
  expect(result).toEqual({ ok: false, error: "gateway down" });
  if (!result.ok) {
    expectTypeOf(result.error).toEqualTypeOf<string>();
  }
});

it.each(["fax", "", "EMAIL"])("an unknown channel name %j returns a failed result", (name) => {
  const { service } = makeService();
  const result = service.send(name, { to: "a@x.com", body: "hi" });
  expect(result.ok).toBe(false);
  if (!result.ok) {
    expect(result.error).toContain(name);
  }
});
