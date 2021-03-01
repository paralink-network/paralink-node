import typing

import sqlalchemy as sa
from sqlalchemy.future import select
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

from src.models import Base
from src.models.exceptions import ActiveChainFailed


class Chain(Base):
    """Chain Model."""

    __tablename__ = "chains"

    name = sa.Column(sa.String, primary_key=True)
    type = sa.Column(sa.String, nullable=False)
    active = sa.Column(sa.Boolean, nullable=False)
    contracts = relationship("Contract")

    __mapper_args__ = {"eager_defaults": True}

    @staticmethod
    async def get_chain(session: Session, chain: str) -> "Chain":
        """Get specified chain.

        Args:
            session (Session):  sqlalchemy session
            chain (str): name of the desired chain

        Returns:
            Chain: Chain model
        """
        result = await session.execute(select(Chain).where(Chain.name == chain))
        return result.scalars().first()

    @staticmethod
    async def get_chains(session: Session) -> typing.List["Chain"]:
        """Get all chains.

        Args:
            session (Session):  sqlalchemy session

        Returns:
            List[Chain]: list of all Chain models
        """
        result = await session.execute(select(Chain))
        return result.scalars().all()

    @staticmethod
    async def set_chain_status(
        session: Session, chain: str, active: bool, chains
    ) -> None:
        """Set chain status.

        Args:
            session (Session):  sqlalchemy session
            chain (str): Name of chain
            active (str): Status update
            chains (Chains): Chains object holding evm and substrate chains
        """
        if active and chain not in {**chains.evm, **chains.substrate}:
            raise ActiveChainFailed(
                f"{chain} could not be activated as it does not exist in chain_config.json or it is disabled."
            )

        await session.execute(
            sa.update(Chain).where(Chain.name == chain).values(active=active)
        )
        await session.commit()

    @staticmethod
    async def reconcile_chains(session: Session, chains) -> None:
        """Reconcile chain data in chain_config.json and database.

        Args:
            session (Session):  sqlalchemy session
            chains: Chains object containing chain data

        Returns:
            List[Chain]: List of Chain objects which have been added
        """
        db_chains = await Chain.get_chains(session)

        # create chain entries in database for new chains in chain_config.json
        new_chains = [
            {
                "name": chain.name,
                "type": chain.type,
                "active": True,
            }
            for _, chain in {**chains.evm, **chains.substrate}.items()
            if chain.name not in [chain.name for chain in db_chains]
        ]
        if new_chains:
            await session.execute(sa.insert(Chain).values(new_chains))

        # if chain is removed / disabled in chain_config.json then update database
        update_chains = [
            chain.name
            for chain in db_chains
            if chain.name not in {**chains.evm, **chains.substrate}
        ]
        if update_chains:
            await session.execute(
                (
                    sa.update(Chain)
                    .where(Chain.name.in_(update_chains))
                    .values(active=False)
                )
            )
        await session.commit()

    def serialise(self) -> dict:
        """Serialise chain.

        Returns:
            dict: serialised chain
        """
        return {
            "name": self.name,
            "type": self.type,
            "active": self.active,
            "contracts": [contract.serialise() for contract in self.contracts],
        }
