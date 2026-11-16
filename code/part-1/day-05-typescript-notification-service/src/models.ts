export interface Notification {
  readonly to: string;
  readonly body: string;
}

export interface Channel {
  send(notification: Notification): void;
}
