/** The part of a fetch Response that fetchUser reads. */
export interface FakeResponse {
  ok: boolean;
  status: number;
  json(): Promise<unknown>;
}

/** A fetch fake that answers every request with the given JSON body. */
export function fakeFetch(body: unknown, status = 200) {
  const urls: string[] = [];
  const fn = async (url: string): Promise<FakeResponse> => {
    urls.push(url);
    return { ok: status >= 200 && status < 300, status, json: async () => body };
  };
  return Object.assign(fn, { urls });
}
