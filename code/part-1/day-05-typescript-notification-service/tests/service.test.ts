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
