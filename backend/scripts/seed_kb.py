import asyncio

from sqlalchemy import select

from backend.database import SessionLocal
from backend.models.kb_article import KBArticle
from backend.routers.kb import index_article

ARTICLES = [
    {
        "title": "Delivery times and costs",
        "category": "shipping",
        "content": "Delivery in Tbilisi is free and takes 1-2 business days. Delivery to other cities in Georgia takes 2-4 business days and costs 10 GEL. Orders placed before 15:00 are usually shipped the same day. Once your order is shipped, its status changes to 'shipped' and you receive a tracking number."
    },
    {
        "title": "How to track your order",
        "category": "shipping",
        "content": "Open My orders in your account to see the status of every order: paid, shipped or delivered. When an order is shipped, a tracking number (for example GE123456) appears on the order card. If your order is shipped but has not arrived within 4 business days, contact support with your order number."
    },
    {
        "title": "Order cancelled or delayed",
        "category": "shipping",
        "content": "An order can be cancelled while its status is 'paid', before it is shipped. If an order was cancelled, the payment is returned to the same card within 3-5 business days. If your order has been in 'paid' status for more than 3 business days, our team will check the warehouse and contact you."
    },
    {
        "title": "Double charge or wrong charge",
        "category": "billing",
        "content": "If you see two charges for one order, the second one is often a temporary authorization that your bank releases within 3-5 business days. If it is still there after 5 days, send us your order number and a screenshot of your bank statement. Our billing team will review it. Refunds are always confirmed by a human from our billing team."
    },
    {
        "title": "Returns and refund policy",
        "category": "billing",
        "content": "You can return a phone within 14 days of delivery if it is unused, in its original box, with all accessories. Activated or damaged phones cannot be returned, but they are still covered by warranty. After we receive and check the returned phone, the refund is decided by our team and sent to your card within 5-7 business days."
    },
    {
        "title": "Payment methods and installments",
        "category": "billing",
        "content": "We accept Visa and Mastercard cards. You can also pay in installments for 6, 12 or 24 months through our partner banks; the bank approves the installment within one business day. The order status becomes 'paid' only after the payment or installment is confirmed."
    },
    {
        "title": "Which storage size should I choose",
        "category": "technical",
        "content": "Storage cannot be upgraded later, so choose carefully. 128 GB is enough if you mostly use messaging, social media and cloud photos. 256 GB is the best choice for most people who take a lot of photos and videos. 512 GB or 1 TB is for people who record a lot of 4K video, play large games or keep everything offline."
    },
    {
        "title": "Battery and charging tips",
        "category": "technical",
        "content": "Charge your new phone with a certified USB-C charger. Both iPhone and Samsung support fast charging with a compatible adapter, which is sold separately. To keep the battery healthy, avoid leaving the phone in heat and use the built-in battery protection setting that limits charging to 80 percent."
    },
    {
        "title": "Phone does not turn on or moving data",
        "category": "technical",
        "content": "If your new phone does not turn on, charge it for 30 minutes and then hold the power button for 10 seconds. To move data from your old phone, iPhone uses Quick Start and Samsung uses Smart Switch: put the two phones next to each other and follow the instructions on the screen. If the phone still does not turn on, contact support."
    },
    {
        "title": "Warranty and screen damage",
        "category": "general",
        "content": "All phones come with an official 1-year manufacturer warranty that covers factory defects. Physical damage like a cracked screen or water damage is not covered by the warranty, but our service center can repair it for a fee. To use the warranty, bring the phone with its receipt or send us your order number."
    },
    {
        "title": "iPhone or Samsung, which one to choose",
        "category": "general",
        "content": "Choose iPhone if you already use other Apple devices like a Mac or AirPods and want a simple experience. Choose Samsung if you want more customization, a built-in S Pen on the Ultra model, or a foldable phone like the Galaxy Z Fold8 or Z Flip8. Pro and Ultra models have the best cameras; the standard models are the best value."
    },
    {
        "title": "Reset your password or change account details",
        "category": "account",
        "content": "If you forgot your password, click 'Forgot password' on the login page and follow the link sent to your email. The link is valid for 1 hour. To change your name or email, contact support from your account. Never share your password with anyone, including our staff."
    },
]


async def main():
    async with SessionLocal() as db:
        for data in ARTICLES:
            existing = await db.scalar(select(KBArticle).where(KBArticle.title == data["title"]))

            if existing:
                print(f"Already exists: {data['title']}")
                continue

            article = KBArticle(**data)
            db.add(article)
            await db.commit()
            await db.refresh(article)

            await index_article(article, db)
            print(f"Added: {article.title}")


if __name__ == "__main__":
    asyncio.run(main())