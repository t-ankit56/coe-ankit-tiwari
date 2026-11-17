import type { Channel, Notification } from "./models";
import { fail, ok, type Result } from "./result";

/** Routes a notification to a channel by name and reports the outcome as a Result. */
export class NotificationService {
  constructor(private readonly channels: Map<string, Channel>) {}

  /** Sends through the named channel; an unknown name or a failing channel gives a failed Result. */
  send(channelName: string, notification: Notification): Result<Notification> {
    const channel = this.channelFor(channelName);
    if (channel === undefined) {
      return fail(`unknown channel "${channelName}"`);
    }
    return this.deliver(channel, notification);
  }

  private channelFor(channelName: string): Channel | undefined {
    return this.channels.get(channelName);
  }

  private deliver(channel: Channel, notification: Notification): Result<Notification> {
    try {
      channel.send(notification);
    } catch (error) {
      return fail(error instanceof Error ? error.message : String(error));
    }
    return ok(notification);
  }
}
