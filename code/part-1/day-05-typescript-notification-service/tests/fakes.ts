import type { Channel, Notification } from "../src/models";
import { NotificationService } from "../src/service";

export class FakeChannel implements Channel {
  sent: Notification[] = [];
  send(notification: Notification): void {
    this.sent.push(notification);
  }
}

export function makeService() {
  const channels = new Map([["email", new FakeChannel()], ["sms", new FakeChannel()]]);
  const service = new NotificationService(channels);
  return { service, channels };
}
