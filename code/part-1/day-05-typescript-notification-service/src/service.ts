import type { Channel, Notification } from "./models";

export class NotificationService {
  constructor(private readonly channels: Map<string, Channel>) {}

  send(channelName: string, notification: Notification): void {
    this.channels.get(channelName)!.send(notification);
  }
}
