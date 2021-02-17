import bcrypt
import sqlalchemy as sa
from sanic import Sanic
from sqlalchemy.future import select
from sqlalchemy.orm import validates

from src.models import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)

    username = sa.Column(sa.String(255), nullable=False, unique=True)
    password_hash = sa.Column(sa.String(255), nullable=False)

    __mapper_args__ = {"eager_defaults": True}

    @validates("username")
    def validate_username(self, key: str, username: str) -> str:
        """Validate username."""
        assert len(username) > 1 and len(username) < 255
        return username

    @validates("password")
    def validate_password(self, key: str, password: str) -> str:
        """Validate password."""
        assert len(password) > 1 and len(password) < 255
        return password

    def set_password(self, password: str) -> None:
        """Calculates password hash and assigns it.

        Args:
            password (str): password string
        """
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Compares `password` hash with current `password_hash`.

        Args:
            password (str): password string

        Returns:
            bool: whether the password matches the hash.
        """
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    @staticmethod
    async def get_user(app: Sanic) -> "User":
        """Gets first user in the DB.

        Args:
            app (Sanic): Sanic app for DB reference

        Returns:
            "User": User model.
        """
        result = await app.db.execute(select(User))
        return result.scalars().first()

    @staticmethod
    async def create_user(app: Sanic, username: str, password: str) -> "User":
        """Creates user in the DB.

        Args:
            app (Sanic): Sanic app
            username (str): username string
            password (str): password string

        Returns:
            "User": User model.
        """
        user = User(username=username)
        user.set_password(password)

        app.db.add(user)
        await app.db.commit()

        return user
