import type { Channel, Notification } from "./models";
import { ok, type Result } from "./result";

export class NotificationService {
  constructor(private readonly channels: Map<string, Channel>) {}

  send(channelName: string, notification: Notification): Result<Notification> {
    this.channels.get(channelName)!.send(notification);
    return ok(notification);
  }
}
