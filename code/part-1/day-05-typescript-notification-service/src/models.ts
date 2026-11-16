/** A message to deliver: who it goes to and what it says. */
export interface Notification {
  readonly to: string;
  readonly body: string;
}

/** Anything that can deliver a notification; throws if it cannot. */
export interface Channel {
  send(notification: Notification): void;
}
