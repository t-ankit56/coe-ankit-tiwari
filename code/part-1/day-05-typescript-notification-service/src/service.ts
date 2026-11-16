import type { Channel, Notification } from "./models";
import { fail, ok, type Result } from "./result";

export class NotificationService {
  constructor(private readonly channels: Map<string, Channel>) {}

  send(channelName: string, notification: Notification): Result<Notification> {
    const channel = this.channelFor(channelName);
    if (channel === undefined) {
      return fail(`unknown channel "${channelName}"`);
    }
    channel.send(notification);
    return ok(notification);
  }

  private channelFor(channelName: string): Channel | undefined {
    return this.channels.get(channelName);
  }
}
