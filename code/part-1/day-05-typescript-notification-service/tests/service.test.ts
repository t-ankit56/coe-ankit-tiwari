import { expect, it } from "vitest";
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
