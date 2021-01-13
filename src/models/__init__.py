from gino import Gino

db = Gino()


class ContractOracle(db.Model):  # type: ignore
    __tablename__ = "contract_oracles"

    id = db.Column(db.String(length=42), primary_key=True)
    active = db.Column(db.Boolean(), default=True)
