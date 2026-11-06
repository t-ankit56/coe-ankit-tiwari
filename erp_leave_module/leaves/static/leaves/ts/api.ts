export const navigation = {
  goTo(url: string): void {
    window.location.assign(url);
  },
};

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  throw new Error("NotImplementedError");
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  throw new Error("NotImplementedError");
}
