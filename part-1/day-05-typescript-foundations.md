# Part 1 · Day 5 — TypeScript for Python Developers: Foundations

**Date completed:** 2026-11-16 · **Time spent:** 15 hours

## Success criteria

| Criterion (copied from the planner) | Done? | Evidence (link or section below) |
| --- | --- | --- |
| Explains how TypeScript differs from Python | Yes | [How TypeScript differs from Python](#how-typescript-differs-from-python) |
| Uses interfaces and union types and generics | Yes | [Interfaces](#interfaces) · [Union types](#union-types) · [Generics](#generics) · [models.ts](../code/part-1/day-05-typescript-notification-service/src/models.ts) · [result.ts](../code/part-1/day-05-typescript-notification-service/src/result.ts) |
| Sets up a TypeScript project with tests | Yes | [Toolchain](#the-typescript-toolchain) · [package.json](../code/part-1/day-05-typescript-notification-service/package.json) · [tsconfig.json](../code/part-1/day-05-typescript-notification-service/tsconfig.json) |
| Rebuilds a small service in TypeScript test-first | Yes | [Exercise 1](#exercise-1-rebuild-notificationservicesend-in-typescript) · [README](../code/part-1/day-05-typescript-notification-service/README.md) |
| Reflects on moving between the two languages | Yes | [Reflection](#reflection) |

## Key learnings

### How TypeScript differs from Python

TypeScript checks types before the code runs, with a compiler (`tsc`), while Python only finds a wrong type when that line runs. The types are erased when the code is compiled to JavaScript, so they never exist at runtime. That is why I run `npm run typecheck` as well as the tests.

### Interfaces

An interface describes the shape of an object: which fields and methods it has. Any object with that shape fits, even if it never says so, which is like a Python `Protocol`. I used one for `Channel`, and `readonly` on `Notification` works like a frozen dataclass, but only the compiler enforces it.

### Union types

A union says a value is one of several types, written with `|`. `Result<T>` is `{ ok: true; value: T } | { ok: false; error: string }`, so checking `result.ok` tells the compiler which field exists. Day 2's `SendResult` used optional fields instead, which allowed impossible combinations.

### Generics

A generic is a type with a blank, like `Result<T>`, where `T` is filled in when it is used. The generic sets the type of the success value, and the union ties `ok` to `value` or `error`. `ok<T>` and `fail<T = never>` are generic functions, and I learned `never` as the default so a plain `fail("x")` fits any `Result`.

### The TypeScript toolchain

Node runs the code and npm installs packages into the project's own `node_modules`, which does the job of a Python venv, so nothing needs activating. `package.json` lists the dependencies and scripts, `tsc` checks types (`strict: true`), and Vitest runs the tests.

## Exercises

### Exercise 1: Rebuild NotificationService.send in TypeScript

Spec: [SPEC.md](../code/part-1/day-05-typescript-notification-service/SPEC.md) · Code and decisions: [README](../code/part-1/day-05-typescript-notification-service/README.md) · Design notes per cycle: [NOTES.md](../code/part-1/day-05-typescript-notification-service/NOTES.md)

I rebuilt only `send` from the Day 2 service, in 8 test-first cycles (10 tests), with a fake channel and no real channels. The commit history shows `test:`, `feat:` and `refactor:` in order for each cycle. Two things differ from Day 2: an unknown channel returns a failed `Result` instead of raising an error, and one `it.each` test covers email and sms together.

## Reflection

The test-first routine felt the same as Python: red, green, refactor, and ZOMBIES for the order. Typescript help us define our object types beforehand which helps in early bug detection, better code understanding, code can be shared within teams without fear of accidental break due to strict type checks. One more difference is that types in python are not enforced by python and we usually find type error when interpreter reaches that line of code but in typescript compilation helps find problems in code early.

## AI use

- **Claude Code:** wrote the spec ([SPEC.md](../code/part-1/day-05-typescript-notification-service/SPEC.md)) in the style of my Day 2, Day 3 and ERP specs, then built the service with me one cycle at a time. It also wrote the project README and the skeleton of this file, and explained generics, `readonly`, why no `venv` is needed and why `send` returns a `Result` instead of throwing.
- **I decided:** to rebuild only `send`, to make `Result<T>` generic, to keep `readonly` on `Notification`, to keep the class-based service for now, to branch from `main`, and to commit as we went from cycle 2.
- **What I corrected:** Claude's first spec was a short summary, so I had it read my earlier specs and rewrite it in their style. I also removed its hardcode-email-then-fail-on-sms steps and had one `it.each` test cover both channels.
- **Claude Code wrote:** the draft of my Key learnings and exercise summary in this file from our conversation. I checked them and changed them. I wrote the reflection myself.
