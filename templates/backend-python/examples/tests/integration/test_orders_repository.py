"""Worked example: repository integration test against real Postgres, tenant isolation and injection safety."""
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from mypkg.data.orders import OrdersRepository

pytestmark = pytest.mark.integration


async def test_list_is_scoped_to_tenant(engine: AsyncEngine) -> None:
    repo = OrdersRepository(engine)
    tenant_a, tenant_b = uuid.uuid4(), uuid.uuid4()
    await repo.insert(tenant_id=tenant_a, status="open", total_cents=1200)
    await repo.insert(tenant_id=tenant_b, status="open", total_cents=999)

    page = await repo.list(tenant_id=tenant_a, status="open", limit=50)

    assert [o.tenant_id for o in page.items] == [tenant_a]


async def test_status_input_is_treated_as_data(engine: AsyncEngine) -> None:
    repo = OrdersRepository(engine)
    tenant = uuid.uuid4()
    await repo.insert(tenant_id=tenant, status="open", total_cents=100)

    page = await repo.list(tenant_id=tenant, status="open' OR '1'='1", limit=50)

    assert page.items == []
