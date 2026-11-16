import type { Channel } from "./models";

export class NotificationService {
  constructor(private readonly channels: Map<string, Channel>) {}
}
