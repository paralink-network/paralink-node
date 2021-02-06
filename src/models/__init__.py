from gino.ext.sanic import Gino

db = Gino()


class Chain(db.Model):  # type: ignore
    __tablename__ = "chains"

    name = db.Column(db.String(length=42), primary_key=True)
    chain_type = db.Column(db.String(length=42))
    url = db.Column(db.String())

    @property
    def serialize(self):
        return {"name": self.name, "type": self.chain_type, "url": self.url}


class ContractOracle(db.Model):  # type: ignore
    __tablename__ = "contract_oracles"

    id = db.Column(db.String(length=42), primary_key=True)
    active = db.Column(db.Boolean(), default=True)
    chain = db.Column(db.String(length=42), db.ForeignKey("chains.name"))

    @property
    def serialize(self):
        return {"id": self.id, "active": self.active, "chain": self.chain}
