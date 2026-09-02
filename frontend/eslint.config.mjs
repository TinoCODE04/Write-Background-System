import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

export default defineConfig([
  ...nextVitals,
  ...nextTypescript,
  {
    // Generated product assets come from the local FastAPI service and change while polling.
    rules: { "@next/next/no-img-element": "off" },
  },
  globalIgnores([".next/**", "next-env.d.ts"]),
]);

