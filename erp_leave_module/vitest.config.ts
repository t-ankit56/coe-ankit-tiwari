import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    include: ["leaves/static/leaves/ts/**/*.test.ts"],
  },
});
