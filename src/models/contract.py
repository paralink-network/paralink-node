import typing

import sqlalchemy as sa
import web3
from sqlalchemy.future import select
from sqlalchemy.orm.session import Session
from substrateinterface.utils.ss58 import is_valid_ss58_address

from src.models import Base
from src.models.chain import Chain
from src.models.exceptions import ChainNotFound, InvalidAddress
from src.network.substrate_chain import SubstrateChain


class Contract(Base):
    """Contract model."""

    __tablename__ = "contracts"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    active = sa.Column(sa.Boolean, nullable=False)
    address = sa.Column(sa.String, nullable=False)
    chain = sa.Column(sa.String, sa.ForeignKey("chains.name"))
    sa.UniqueConstraint(address, chain, name="uix_1")

    __mapper_args__ = {"eager_defaults": True}

    @staticmethod
    async def get_contract(session: Session, id: int) -> "Contract":
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
        session: Session, address: str, active: bool, chain: str
    ) -> None:
        """Create contract entry in db.

        Args:
            session (Session): sqlalchemy session
            address (str): contract address
            active (bool): contract status
            chain (str): chain the contract is associated with

        Raises:
            ChainNotFound: raised if the chain specified does not exist in the db
            InvalidAddress: raised if the address is not valid for the chain specified
        """
        chain_data = await Chain.get_chain(session, chain)
        if not chain_data:
            raise ChainNotFound(f"Chain not found: {chain}")

        if (chain_data.type == "evm" and not web3.Web3.isAddress(address)) or (
            chain_data.type == "substrate"
            and not is_valid_ss58_address(
                address, SubstrateChain.get_ss58_prefix(chain)
            )
        ):
            raise InvalidAddress(
                f"Invalid address for chain: {chain} - address: {address}"
            )

        await session.execute(
            sa.insert(Contract).values(address=address, active=active, chain=chain)
        )
        await session.commit()

    @staticmethod
    async def set_contract_status(session: Session, id: int, active: bool) -> None:
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
    async def delete_contract(session: Session, id: int) -> None:
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
        return {
            "id": self.id,
            "chain": self.chain,
            "active": self.active,
            "address": self.address,
        }
