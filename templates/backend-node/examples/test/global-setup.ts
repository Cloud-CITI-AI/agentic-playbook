// Worked example: one real Postgres per test run via Testcontainers (BE-9). Requires Docker.
import { PostgreSqlContainer, type StartedPostgreSqlContainer } from "@testcontainers/postgresql";
import { runMigrations } from "../src/data/migrate";

let container: StartedPostgreSqlContainer;

export async function setup() {
  container = await new PostgreSqlContainer("postgres:17-alpine").start();  // pin the same major as production
  process.env.DATABASE_URL = container.getConnectionUri();
  await runMigrations(process.env.DATABASE_URL);
}

export async function teardown() {
  await container?.stop();
}
