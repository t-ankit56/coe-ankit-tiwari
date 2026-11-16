import type { Channel, Notification } from "../src/models";
import { NotificationService } from "../src/service";

export class FakeChannel implements Channel {
  sent: Notification[] = [];

  constructor(private readonly failWith?: string) {}

  send(notification: Notification): void {
    if (this.failWith !== undefined) {
      throw new Error(this.failWith);
    }
    this.sent.push(notification);
  }
}

export function makeService() {
  const channels = new Map([["email", new FakeChannel()], ["sms", new FakeChannel()]]);
  const service = new NotificationService(channels);
  return { service, channels };
}
