from uuid import uuid4

from slitherway.commands import migrate
from slitherway.models import FlywayCommandArgs
from sqlmodel import Session, create_engine, select
from testcontainers.postgres import PostgresContainer

from src.persistence.models import Author, Book


def test_can_insert_book():
    with PostgresContainer("postgres:14") as pg:
        # Arrange
        args = FlywayCommandArgs(
            user=pg.POSTGRES_USER,
            password=pg.POSTGRES_PASSWORD,
            locations=["migrations"],
            url=f"jdbc:postgresql://localhost:{pg.get_exposed_port(5432)}/{pg.POSTGRES_DB}",
        )

        migrate(args)
        engine = create_engine(
            f"postgresql://"
            f"{pg.POSTGRES_USER}:{pg.POSTGRES_PASSWORD}"
            f"@localhost:{pg.get_exposed_port(5432)}"
            f"/{pg.POSTGRES_DB}",
            echo=True,
        )

        with Session(engine) as session:
            # Act
            author = Author(id=uuid4(), name="Brando Sando")

            book = Book(
                id=uuid4(),
                author_id=author.id,
                isbn="1234-56-789",
                title="The Final Empire",
                price=13.37,
            )

            session.add(author)
            session.add(book)
            session.commit()

            # Assert
            statement = select(Book)
            results = session.exec(statement)
            retrieved_book = results.first()
            assert retrieved_book.title == book.title
            # assert retrieved_book.author.name == author.name


def test_can_query_books_by_author():
    with PostgresContainer("postgres:14") as pg:
        # Arrange
        args = FlywayCommandArgs(
            user=pg.POSTGRES_USER,
            password=pg.POSTGRES_PASSWORD,
            locations=["migrations"],
            url=f"jdbc:postgresql://localhost:{pg.get_exposed_port(5432)}/{pg.POSTGRES_DB}",
        )

        migrate(args)
        engine = create_engine(
            f"postgresql://"
            f"{pg.POSTGRES_USER}:{pg.POSTGRES_PASSWORD}"
            f"@localhost:{pg.get_exposed_port(5432)}"
            f"/{pg.POSTGRES_DB}",
            echo=True,
        )

        with Session(engine) as session:
            # Act
            author = Author(id=uuid4(), name="Brando Sando")

            book_a = Book(
                id=uuid4(),
                author_id=author.id,
                isbn="1234-56-789",
                title="The Final Empire",
                price=13.37,
            )

            book_b = Book(
                id=uuid4(),
                author_id=author.id,
                isbn="1234-56-987",
                title="The Lost Metal",
                price=13.37,
            )

            session.add(author)
            session.add(book_a)
            session.add(book_b)
            session.commit()

            # Assert
            statement = select(Book).join(Author).where(Author.name == author.name)
            result = session.exec(statement).all()
            assert len(result) == 2
