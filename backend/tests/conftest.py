import os
import uuid

import pytest
from fastapi.testclient import TestClient

import backend.agents as agents
from backend.main import app
from backend.schemas.triage import TriageResult, DraftReply, QualityCheckResult


class FakeStructuredLLM:
    def __init__(self, schema):
        self.schema = schema

    async def ainvoke(self, prompt):
        text = str(prompt[-1].content).lower()

        if self.schema is TriageResult:
            if "buy cheap" in text:
                return TriageResult(category="spam", priority="low", sentiment="neutral",
                                    language="en", summary="Spam", classification_confidence=0.95)
            if "twice" in text:
                return TriageResult(category="billing", priority="urgent", sentiment="angry",
                                    language="en", summary="Charged twice", classification_confidence=0.9)
            return TriageResult(category="account", priority="low", sentiment="neutral",
                                language="en", summary="Forgot password", classification_confidence=0.9)

        if self.schema is DraftReply:
            return DraftReply(draft_reply="Go to the login page and click Forgot password.",
                              draft_confidence=0.9, cited_article_ids=[1])

        return QualityCheckResult(is_acceptable=True, issues=[])


class FakeLLM:
    def with_structured_output(self, schema):
        return FakeStructuredLLM(schema)


class FakeDocument:
    page_content = "Go to the login page and click Forgot password."
    metadata = {"article_id": 1, "title": "Reset password"}


class FakeVectorStore:
    async def asimilarity_search_with_relevance_scores(self, query, k=4, filter=None):
        return [(FakeDocument(), 0.85)]


@pytest.fixture(scope="session")
def client():
    agents.llm = FakeLLM()
    agents.vector_store = FakeVectorStore()

    with TestClient(app) as test_client:
        yield test_client


def login(client, email, password):
    response = client.post("/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200, f"Login failed for {email}: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def costumer(client):
    email = f"test-{uuid.uuid4().hex[:8]}@test.ge"
    client.post("/auth/register", json={"email": email, "full_name": "Test User", "password": "test123"})
    return login(client, email, "test123")


@pytest.fixture
def admin(client):
    return login(client, os.getenv("ADMIN_EMAIL"), os.getenv("ADMIN_PASSWORD"))