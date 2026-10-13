// Worked example: repository integration test against real Postgres. Each test isolates data by tenant.
import { randomUUID } from "node:crypto";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { createDb, type Db } from "../src/data/db";
import { OrdersRepository } from "../src/data/orders.repository";

describe("OrdersRepository (integration)", () => {
  let db: Db;
  let repo: OrdersRepository;
  const tenantA = randomUUID();
  const tenantB = randomUUID();

  beforeAll(async () => {
    db = createDb(process.env.DATABASE_URL!);
    repo = new OrdersRepository(db);
    await repo.insert({ tenantId: tenantA, status: "open", totalCents: 1200 });
    await repo.insert({ tenantId: tenantA, status: "closed", totalCents: 800 });
    await repo.insert({ tenantId: tenantB, status: "open", totalCents: 999 });
  });

  afterAll(async () => db.destroy());

  it("returns only the caller's tenant's orders (BE-5 tenant scoping)", async () => {
    const page = await repo.list({ tenantId: tenantA, status: "open", limit: 50 });
    expect(page.items).toHaveLength(1);
    expect(page.items.every((o) => o.tenantId === tenantA)).toBe(true);
  });

  it("paginates with a stable cursor", async () => {
    const first = await repo.list({ tenantId: tenantA, limit: 1 });
    const second = await repo.list({ tenantId: tenantA, limit: 1, cursor: first.nextCursor });
    expect(first.items[0]!.id).not.toEqual(second.items[0]!.id);
    expect(second.nextCursor).toBeNull();
  });

  it("treats user input as data, not SQL", async () => {
    const page = await repo.list({ tenantId: tenantA, status: "open' OR '1'='1" as never, limit: 50 });
    expect(page.items).toHaveLength(0);
  });
});
