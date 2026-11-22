import uuid
import asyncio

from sqlalchemy import select

import backend.agents as agents
from backend.database import SessionLocal
from backend.models.user import User
from backend.models.order import Order


def test_costumer_cannot_use_admin_endpoints(client, costumer, admin):
    response = client.get("/auth/users", headers=costumer)
    assert response.status_code == 403

    response = client.get("/auth/users", headers=admin)
    assert response.status_code == 200

    response = client.get("/auth/users")
    assert response.status_code == 401


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


def register(client):
    email = f"test-{uuid.uuid4().hex[:8]}@test.ge"
    client.post("/auth/register", json={"email": email, "full_name": "Test User", "password": "test123"})
    response = client.post("/auth/login", data={"username": email, "password": "test123"})
    return email, {"Authorization": f"Bearer {response.json()['access_token']}"}


async def add_order(email, number):
    async with SessionLocal() as db:
        user = await db.scalar(select(User).where(User.email == email))
        db.add(Order(order_number=number, costumer_id=user.id, product="iPhone 17 Pro",
                     total=3799, status="shipped", tracking_number="GE123456"))
        await db.commit()


def test_costumer_can_buy_and_sees_only_own_orders(client, admin):
    owner_email, owner = register(client)
    other_email, other = register(client)

    response = client.post("/orders", json={"product": "iPhone 17 Pro"}, headers=owner)
    assert response.status_code == 201
    assert response.json()["status"] == "paid"
    assert response.json()["total"] == 3799
    order_id = response.json()["id"]

    assert [o["id"] for o in client.get("/orders/my", headers=owner).json()] == [order_id]
    assert client.get("/orders/my", headers=other).json() == []
    assert client.get("/orders", headers=owner).status_code == 403

    response = client.patch(f"/orders/{order_id}", json={"status": "shipped", "tracking_number": "GE111222"}, headers=admin)
    assert response.json()["status"] == "shipped"


def test_ai_finds_only_own_order(client):
    owner_email, owner = register(client)
    other_email, other = register(client)
    number = str(uuid.uuid4().int)[:8]

    client.portal.call(add_order, owner_email, number)

    state = {"subject": "Where is my phone?", "body": f"Order #{number}", "costumer_email": owner_email}
    result = client.portal.call(agents.find_order, state)
    assert "GE123456" in result["order_info"]

    state["costumer_email"] = other_email
    result = client.portal.call(agents.find_order, state)
    assert "not found" in result["order_info"]
    assert "GE123456" not in result["order_info"]


def test_ai_answers_follow_up_message(client, costumer):
    response = client.post("/tickets/", json={"subject": "Forgot password", "body": "I forgot my password"}, headers=costumer)
    ticket_id = response.json()["id"]
    assert client.get(f"/tickets/{ticket_id}", headers=costumer).json()["status"] == "replied"

    response = client.post(f"/tickets/{ticket_id}/messages", json={"content": "And how do I change my email?"}, headers=costumer)
    assert response.status_code == 201

    ticket = client.get(f"/tickets/{ticket_id}", headers=costumer).json()
    assert ticket["status"] == "replied"
    assert [m["author_type"] for m in ticket["messages"]] == ["ai", "costumer", "ai"]