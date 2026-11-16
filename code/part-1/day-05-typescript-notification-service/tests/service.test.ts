import { expect, it } from "vitest";
import type { Channel, Notification } from "../src/models";
import { NotificationService } from "../src/service";

class FakeChannel implements Channel {
  sent: Notification[] = [];
  send(notification: Notification): void {
    this.sent.push(notification);
  }
}

it("a new service has sent nothing", () => {
  const email = new FakeChannel();
  const sms = new FakeChannel();
  new NotificationService(new Map([["email", email], ["sms", sms]]));
  expect(email.sent).toEqual([]);
  expect(sms.sent).toEqual([]);
});

it.each(["email", "sms"])("sending through %s reaches only that channel", (name) => {
  const channels = new Map([["email", new FakeChannel()], ["sms", new FakeChannel()]]);
  const service = new NotificationService(channels);
  const notification = { to: "someone", body: "hi" };
  service.send(name, notification);
  for (const [channelName, channel] of channels) {
    expect(channel.sent).toEqual(channelName === name ? [notification] : []);
  }
});
