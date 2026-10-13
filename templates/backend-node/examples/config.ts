// Worked example: config parsed once, fail fast (BE-2).
import { z } from "zod";

const Config = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]),
  PORT: z.coerce.number().int().min(1).max(65535).default(8080),
  DATABASE_URL: z.string().url(),
  LOG_LEVEL: z.enum(["debug", "info", "warn", "error"]).default("info"),
  OUTBOUND_TIMEOUT_MS: z.coerce.number().int().positive().default(2000),
});
export type Config = z.infer<typeof Config>;

export function loadConfig(env: NodeJS.ProcessEnv = process.env): Config {
  const parsed = Config.safeParse(env);
  if (!parsed.success) {
    // Print variable names only, never values.
    console.error("Invalid configuration:", parsed.error.issues.map((i) => i.path.join(".")).join(", "));
    process.exit(1);
  }
  return parsed.data;
}
