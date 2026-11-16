import type { Channel, Notification } from "./models";
import { fail, ok, type Result } from "./result";

export class NotificationService {
  constructor(private readonly channels: Map<string, Channel>) {}

  send(channelName: string, notification: Notification): Result<Notification> {
    const channel = this.channels.get(channelName);
    if (channel === undefined) {
      return fail(`unknown channel "${channelName}"`);
    }
    channel.send(notification);
    return ok(notification);
  }
}
