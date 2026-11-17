/** The fields of a JSONPlaceholder user that this module uses. */
export interface User {
  readonly id: number;
  readonly name: string;
  readonly email: string;
  readonly address: { readonly city: string };
}
