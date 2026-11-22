import asyncio

from sqlalchemy import select

from backend.database import SessionLocal
from backend.models.kb_article import KBArticle
from backend.routers.kb import index_article

ARTICLES = [
    {
        "title": "How to reset your password",
        "category": "account",
        "content": "If you forgot your password, go to the login page and click 'Forgot password'. Enter the email address linked to your account. You will receive a reset link within 5 minutes. The link is valid for 1 hour. If you do not see the email, check your spam folder. After clicking the link, choose a new password with at least 8 characters."
    },
    {
        "title": "Account hacked or suspicious login",
        "category": "account",
        "content": "If you think someone else has access to your account, reset your password immediately and log out of all devices from Settings > Security. Turn on two-factor authentication. Our security team reviews every hacked account report within 2 hours. Never share your password or verification codes with anyone, including our staff."
    },
    {
        "title": "How to change your email address",
        "category": "account",
        "content": "To change your email address, go to Settings > Profile and click 'Change email'. Enter the new email address and confirm it with the code we send to that address. Your old email will stop working for login right after the change. If you no longer have access to your old email, contact support."
    },
    {
        "title": "Payment methods we accept",
        "category": "billing",
        "content": "We accept Visa, Mastercard and American Express cards, as well as PayPal and Apple Pay. Payments are processed securely and we never store your full card number. If your payment fails, check that the card is not expired, that you have enough balance, and that your bank allows online payments."
    },
    {
        "title": "Double charge or wrong charge",
        "category": "billing",
        "content": "If you see two charges for one order, the second one is often a temporary authorization that your bank releases within 3-5 business days. If the charge is still there after 5 business days, send us the order number and a screenshot of your bank statement. Our billing team will review the case. Refunds are decided only by the billing team after review."
    },
    {
        "title": "Refund policy",
        "category": "billing",
        "content": "You can request a refund within 14 days of delivery if the product is unused and in its original packaging. Refund requests are reviewed by our billing team, usually within 3 business days. If approved, the money is returned to the original payment method within 5-10 business days. Digital products cannot be refunded after download."
    },
    {
        "title": "Order delivery times",
        "category": "shipping",
        "content": "Standard delivery takes 3-7 business days. Express delivery takes 1-2 business days. Delivery times can be longer during holidays. You receive a tracking number by email as soon as your order is shipped. If your order is delayed more than 7 days, contact support with your order number."
    },
    {
        "title": "How to track your order",
        "category": "shipping",
        "content": "To track your order, open the shipping confirmation email and click the tracking link, or go to My Orders in your account and click 'Track'. Tracking information can take up to 24 hours to appear after shipping. If tracking shows 'delivered' but you did not receive the package, check with neighbours and contact support within 48 hours."
    },
    {
        "title": "App crashes or does not load",
        "category": "technical",
        "content": "If the app crashes or does not load, first make sure you have the latest version installed. Restart your device and check your internet connection. Clearing the app cache often fixes loading problems: go to your phone Settings > Apps > our app > Clear cache. If the problem continues, send us your device model and app version."
    },
    {
        "title": "Website errors and login problems",
        "category": "technical",
        "content": "If the website shows an error or you cannot log in, try clearing your browser cookies and cache, or open the site in a private window. Make sure your browser is updated. Disable browser extensions such as ad blockers, as they can block the login page. If you still see the error, send us a screenshot of it."
    },
    {
        "title": "Contact us and working hours",
        "category": "general",
        "content": "Our support team works Monday to Friday, 9:00 to 18:00. You can contact us by creating a ticket in your account. Most tickets get a first reply within 24 hours. Urgent issues such as hacked accounts or double charges are handled first."
    },
    {
        "title": "How to give feedback or suggestions",
        "category": "general",
        "content": "We love hearing your ideas. You can send feedback or feature suggestions by creating a ticket with the subject 'Feedback'. Our product team reads every suggestion. We cannot reply to each one personally, but popular ideas are added to our roadmap."
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