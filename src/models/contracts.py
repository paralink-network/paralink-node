import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative.api import DeclarativeMeta

Base: DeclarativeMeta = declarative_base()


class ContractOracle(Base):
    __tablename__ = "contract_oracles"

    id = sa.Column(sa.String(length=42), primary_key=True)
    active = sa.Column(sa.Boolean(), default=True)

    __mapper_args__ = {"eager_defaults": True}
