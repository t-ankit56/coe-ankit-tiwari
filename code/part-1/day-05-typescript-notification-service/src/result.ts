/** Either a success carrying a value or a failure carrying an error message. */
export type Result<T> =
  | { ok: true; value: T }
  | { ok: false; error: string };

/** Builds a successful Result that carries the given value. */
export function ok<T>(value: T): Result<T> {
  return { ok: true, value };
}

/** Builds a failed Result that carries an error message and no value. */
export function fail<T = never>(error: string): Result<T> {
  return { ok: false, error };
}
