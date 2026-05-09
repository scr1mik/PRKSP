from app.main import initialize_database_schema


class FakeDialect:
    name = "postgresql"


class FakeConnection:
    def __init__(self) -> None:
        self.statements: list[str] = []

    def execute(self, statement) -> None:
        self.statements.append(str(statement))


class FakeTransaction:
    def __init__(self, connection: FakeConnection) -> None:
        self.connection = connection

    def __enter__(self) -> FakeConnection:
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None


class FakeEngine:
    dialect = FakeDialect()

    def __init__(self) -> None:
        self.connection = FakeConnection()

    def begin(self) -> FakeTransaction:
        return FakeTransaction(self.connection)


def test_postgres_schema_initialization_uses_advisory_lock(monkeypatch) -> None:
    engine = FakeEngine()
    create_all_binds = []

    monkeypatch.setattr(
        "app.main.Base.metadata.create_all",
        lambda bind: create_all_binds.append(bind),
    )

    initialize_database_schema(engine)

    assert any("pg_advisory_lock" in statement for statement in engine.connection.statements)
    assert any("pg_advisory_unlock" in statement for statement in engine.connection.statements)
    assert create_all_binds == [engine.connection]
