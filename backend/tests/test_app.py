import uuid

import asyncio


def test_register_and_login(client):
    email = f"test-{uuid.uuid4().hex[:8]}@test.ge"

    response = client.post("/auth/register", json={
        "email": email,
        "full_name": "Test User",
        "password": "test123"
    })
    assert response.status_code in (200, 201)
    assert response.json()["role"] == "costumer"

    response = client.post("/auth/login", data={"username": email, "password": "test123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_costumer_cannot_use_admin_endpoints(client, costumer, admin):
    response = client.get("/auth/users", headers=costumer)
    assert response.status_code == 403

    response = client.get("/auth/users", headers=admin)
    assert response.status_code == 200

    response = client.get("/auth/users")
    assert response.status_code == 401

def test_create_ticket(client, costumer, admin):
    response = client.post("/tickets/", json={
        "subject": "Forgot password",
        "body": "I forgot my password"
    }, headers=costumer)
    assert response.status_code == 201
    assert response.json()["status"] == "triaging"

    response = client.post("/tickets/", json={
        "subject": "Test",
        "body": "Admin should not create tickets"
    }, headers=admin)
    assert response.status_code == 403

def test_simple_ticket_is_auto_replied(client, costumer):
    response = client.post("/tickets/", json={
        "subject": "Forgot password",
        "body": "I forgot my password, how can I reset it?"
    }, headers=costumer)
    ticket_id = response.json()["id"]

    ticket = client.get(f"/tickets/{ticket_id}", headers=costumer).json()

    assert ticket["status"] == "replied"
    assert ticket["category"] == "account"
    assert ticket["messages"][0]["author_type"] == "ai"

def test_billing_ticket_waits_for_review(client, costumer, admin):
    response = client.post("/tickets/", json={
        "subject": "Charged twice",
        "body": "You charged me twice for my order!"
    }, headers=costumer)
    ticket_id = response.json()["id"]

    ticket = client.get(f"/tickets/{ticket_id}", headers=costumer).json()

    assert ticket["status"] == "awaiting_review"
    assert ticket["category"] == "billing"
    assert ticket["messages"] == []

    queue = client.get("/review/queue", headers=admin).json()
    assert ticket_id in [item["id"] for item in queue]

def test_agent_approves_reply(client, costumer, admin):
    response = client.post("/tickets/", json={
        "subject": "Charged twice",
        "body": "You charged me twice for my order!"
    }, headers=costumer)
    ticket_id = response.json()["id"]

    response = client.post(f"/review/{ticket_id}/decision", json={"decision": "approve"}, headers=admin)
    assert response.status_code == 200
    assert response.json()["status"] == "replied"

    ticket = client.get(f"/tickets/{ticket_id}", headers=costumer).json()
    assert ticket["status"] == "replied"
    assert len(ticket["messages"]) == 1

def test_agent_rejects_reply(client, costumer, admin):
    response = client.post("/tickets/", json={
        "subject": "Charged twice",
        "body": "You charged me twice for my order!"
    }, headers=costumer)
    ticket_id = response.json()["id"]

    response = client.post(f"/review/{ticket_id}/decision", json={"decision": "reject"}, headers=admin)
    assert response.json()["status"] == "escalated"

    ticket = client.get(f"/tickets/{ticket_id}", headers=costumer).json()
    assert ticket["status"] == "escalated"
    assert ticket["priority"] == "urgent"
    assert ticket["messages"] == []

    response = client.post(f"/review/{ticket_id}/decision", json={"decision": "approve"}, headers=admin)
    assert response.status_code == 409

def test_spam_ticket(client, costumer):
    response = client.post("/tickets/", json={
        "subject": "Great offer",
        "body": "Buy cheap watches now at our website!!!"
    }, headers=costumer)
    ticket_id = response.json()["id"]

    ticket = client.get(f"/tickets/{ticket_id}", headers=costumer).json()

    assert ticket["status"] == "spam"
    assert ticket["messages"] == []


def test_personal_data_is_hidden():
    from backend.agents import prepare_ticket

    result = asyncio.run(prepare_ticket({
        "subject": "Payment problem",
        "body": "My card is 4111 1111 1111 1234, email nino@gmail.com, phone +995 555 123 456"
    }))

    assert "4111 **** **** 1234" in result["body"]
    assert "1111 1111" not in result["body"]
    assert "[email]" in result["body"]
    assert "nino@gmail.com" not in result["body"]
    assert "[phone]" in result["body"]