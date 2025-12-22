import pytest

from app.application.uow.unit_of_work import UnitOfWork


class FakeUnitOfWork(UnitOfWork):
    def __init__(self):
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


@pytest.fixture
def uow():
    return FakeUnitOfWork()
