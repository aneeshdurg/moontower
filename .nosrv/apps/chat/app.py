#!/home/aneesh/public/.nosrv/pydb/bin/python
import base64
import json
import sys
from datetime import UTC, datetime, timedelta

import click
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

root = "/home/aneesh/public/.nosrv/apps/chat/"
engine = create_engine(f"sqlite:///{root}/chat.sqlite3")


class Base(DeclarativeBase):
    pass


class Message(Base):
    __tablename__ = "Message"

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[bytes]
    timestamp: Mapped[datetime]
    # sender_ip: Mapped[str]
    # sender_name: Mapped[str]

    def __repr__(self):
        return json.dumps(
            {
                "id": self.id,
                "timestamp": str(self.timestamp),
                "message": base64.b64encode(self.message).decode(),
            }
        )


@click.group()
def cli():
    """Run chat"""


@cli.command("createdb")
def createdb():
    Base.metadata.create_all(engine)


@cli.command("message")
def add():
    message = sys.stdin.buffer.read()
    with Session(engine) as session:
        session.add(Message(message=message, timestamp=datetime.now(UTC)))
        session.commit()


@cli.command("view")
@click.option("--since", type=str, default=None)
def view(since: str | None):
    if since is None:
        since = "1970-01-01 00:00:00.00"
    since = datetime.strptime(since, "%Y-%m-%d %H:%M:%S.%f")
    with Session(engine) as session:
        for msg in session.scalars(
            sa.select(Message)
            .where(Message.timestamp > since)
            .order_by(Message.timestamp.asc())
        ).all():
            print(msg)


@cli.command("prune")
@click.option("--since", type=str, default=None)
def prune(since: str | None):
    # TODO - prune should only keep the most recent `n` messages instead of time
    # based memory
    if since is None:
        delta = timedelta(minutes=-5)
        since = datetime.now(UTC) + delta
    else:
        since = datetime.strptime(since, "%Y-%m-%d %H:%M:%S.%f")
    with Session(engine) as session:
        session.execute(sa.delete(Message).where(Message.timestamp <= since))
        session.commit()


"""
@cli.command("delete")
@click.argument("service", type=str)
def delete(service: str):
    with Session(engine) as session:
        session.execute(
            sa.delete(AccessCounter).where(AccessCounter.service == service)
        )
        session.commit()


@cli.command("view")
@click.option("--service", type=str, default=None)
def view(service: str | None):
    with Session(engine) as session:
        if service is None:
            for ctr in session.scalars(sa.select(AccessCounter)).all():
                print(f"{ctr.service} = {ctr.counter}")
        else:
            ctr = session.scalars(
                sa.select(AccessCounter).where(AccessCounter.service == service)
            ).first()
            print(ctr.counter)

"""

if __name__ == "__main__":
    cli()
