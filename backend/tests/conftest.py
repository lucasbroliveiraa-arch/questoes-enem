"""
Fixtures compartilhadas dos testes. Os testes rodam contra SQLite em memória
(via override da dependency get_db) em vez do Postgres real — mais rápido e
sem exigir um banco de fato para rodar `pytest`. A aplicação em si continua
usando Postgres em dev/produção.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.question import Question

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture()
def db_session():
    # StaticPool: mantém uma única conexão viva, senão cada checkout do pool
    # abriria um banco :memory: novo e vazio (SQLite não persiste em disco).
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_question(db_session):
    question = Question(
        year=2023,
        area="Matemática",
        number=1,
        context="Contexto de exemplo.",
        statement="Quanto é 2 + 2?",
        option_a="3",
        option_b="4",
        option_c="5",
        option_d="6",
        option_e="7",
        correct_answer="B",
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question
