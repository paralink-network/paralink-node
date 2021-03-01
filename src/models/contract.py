import typing

import sqlalchemy as sa
from sqlalchemy.future import select
from sqlalchemy.orm.session import Session

from src.models import Base


class Contract(Base):
    """Contract model."""

    __tablename__ = "contracts"

    id = sa.Column(sa.String, primary_key=True)
    active = sa.Column(sa.Boolean, nullable=False)
    chain = sa.Column(sa.String, sa.ForeignKey("chains.name"))

    __mapper_args__ = {"eager_defaults": True}

    @staticmethod
    async def get_contract(session: Session, id: str) -> "Contract":
        """Get specified contract.

        Args:
            session (Session):  sqlalchemy session
            id (str): contract identifier

        Returns:
            Contract: Contract model
        """
        result = await session.execute(select(Contract).where(Contract.id == id))
        return result.scalars().first()

    @staticmethod
    async def get_contracts(
        session: Session, chain: typing.Optional[str] = None
    ) -> typing.List["Contract"]:
        """Get contracts.

        Args:
            session (Session): sqlalchemy session
            chain (Optional[str]): chain name

        Returns:
            List[Contract]: List of Contract objects
        """
        if chain:
            result = await session.execute(
                select(Contract).where(Contract.chain == chain)
            )
        else:
            result = await session.execute(select(Contract))
        return result.scalars().all()

    @staticmethod
    async def create_contract(
        session: Session, id: str, active: bool, chain: str
    ) -> None:
        """Create contract entry in db.

        Args:
            session (Session):  sqlalchemy session
            id (str): contract identifier
            active (bool): contract status
            chain (str): chain the contract is associated with
        """
        await session.execute(
            sa.insert(Contract).values(id=id, active=active, chain=chain)
        )
        await session.commit()

    @staticmethod
    async def set_contract_status(session: Session, id: str, active: bool) -> None:
        """Set contract status.

        Args:
            session (Session):  sqlalchemy session
            id (str): contract identifier
            active (bool): contract status
        """
        await session.execute(
            sa.update(Contract).where(Contract.id == id).values(active=active)
        )
        await session.commit()

    @staticmethod
    async def delete_contract(session: Session, id: str) -> None:
        """Delete contract.

        Args:
            session (Session): sqlalchemy session
            id (str): contract id
        """
        await session.execute(sa.delete(Contract).where(Contract.id == id))
        await session.commit()

    def serialise(self):
        """Serialise contract.

        Returns:
            dict: serialised contract
        """
        return {"id": self.id, "chain": self.chain, "active": self.active}
