#!/home/aneesh/public/.nosrv/pydb/bin/python
import click

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

root = "/home/aneesh/public/.nosrv/accesscounter"
engine = create_engine(f"sqlite:///{root}/accesscounter.sqlite3")


class Base(DeclarativeBase):
    pass


class AccessCounter(Base):
    __tablename__ = "AccessCounter"

    service: Mapped[str] = mapped_column(primary_key=True)
    counter: Mapped[int]

    def __repr__(self):
        return f"AccessCounter(service={self.id}, counter={self.counter})"


@click.group()
def cli():
    """Run accesscounter"""


@cli.command("createdb")
def createdb():
    Base.metadata.create_all(engine)


@cli.command("add")
@click.argument("service", type=str)
def add(service: str):
    with Session(engine) as session:
        session.add(AccessCounter(service=service, counter=0))
        session.commit()


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


@cli.command("touch")
@click.argument("service", type=str)
@click.option("--reset", type=bool, is_flag=True, default=False)
def touch(service: str, reset: bool):
    with Session(engine) as session:
        ctr = session.scalars(
            sa.select(AccessCounter).where(AccessCounter.service == service)
        ).first()
        if reset:
            ctr.counter = 0
        else:
            ctr.counter += 1
        print(ctr.counter)
        session.merge(ctr)
        session.commit()


if __name__ == "__main__":
    cli()
