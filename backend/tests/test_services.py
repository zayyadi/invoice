import os
import asyncio
import tempfile
import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal

os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret"

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus
from app.models.payment import Payment
from app.models.user import User
from app.schemas.auth import UserLogin, UserRegister, UserUpdate
from app.schemas.client import ClientCreate, ClientUpdate
from app.schemas.invoice import InvoiceCreate, InvoiceItemCreate, InvoiceUpdate
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.services import auth_service, client_service, dashboard_service
from app.services.export_service import generate_pdf
from app.services.file_service import save_logo_for_invoice
from app.services.invoice_service import create_invoice
from app.services.invoice_service import update_invoice
from app.services.invoice_status_service import (
    check_and_mark_overdue,
    get_status_history,
    mark_as_cancelled,
    mark_as_paid,
    mark_as_sent,
    mark_as_viewed,
    transition_status,
)
from app.services.payment_service import (
    create_payment,
    delete_payment,
    get_payment_summary,
    update_payment,
)


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.db = self.SessionLocal()
        self.user = self.create_user("owner@example.com", "Owner")
        self.other_user = self.create_user("other@example.com", "Other")

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()

    def create_user(self, email, full_name, **overrides):
        user = User(
            email=email,
            password_hash=overrides.pop("password_hash", "hash"),
            full_name=full_name,
            company_name=overrides.pop("company_name", None),
            phone=overrides.pop("phone", None),
            default_currency=overrides.pop("default_currency", "NGN"),
            is_active=overrides.pop("is_active", True),
            email_verified=overrides.pop("email_verified", False),
            **overrides,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_invoice_row(
        self,
        user,
        *,
        invoice_number,
        status=InvoiceStatus.DRAFT,
        total=Decimal("100.00"),
        paid=Decimal("0.00"),
        issue_date=None,
        due_date=None,
        client=None,
        created_at=None,
    ):
        invoice = Invoice(
            user_id=user.id,
            client_id=client.id if client else None,
            invoice_number=invoice_number,
            status=status,
            issuer_name=user.full_name,
            customer_name="Ada Client",
            customer_email="ada@example.com",
            issue_date=issue_date or date.today(),
            due_date=due_date or date.today() + timedelta(days=14),
            currency="NGN",
            tax_rate=Decimal("0.00"),
            subtotal=total,
            tax_amount=Decimal("0.00"),
            total_amount=total,
            paid_amount=paid,
            created_at=created_at or datetime.utcnow(),
        )
        invoice.items = [
            InvoiceItem(
                description="Service",
                quantity=1,
                unit_price=total,
                line_total=total,
            )
        ]
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def create_payment_row(self, invoice, amount, payment_date=None):
        payment = Payment(
            user_id=invoice.user_id,
            invoice_id=invoice.id,
            amount=Decimal(amount),
            payment_date=payment_date or date.today(),
            payment_method="bank_transfer",
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment


class AuthServiceTests(DatabaseTestCase):
    def test_register_authenticate_refresh_update_and_change_password(self):
        payload = UserRegister(
            email="new@example.com",
            password="password123",
            full_name="New User",
            company_name="New Co",
            phone="+2348000000000",
        )

        user = auth_service.register_user(self.db, payload)

        self.assertEqual(user.email, "new@example.com")
        self.assertNotEqual(user.password_hash, "password123")
        self.assertTrue(auth_service.authenticate_user(
            self.db, UserLogin(email="new@example.com", password="password123")
        ))

        tokens = auth_service.create_tokens(user)
        self.assertEqual(tokens["token_type"], "bearer")
        self.assertIn("access_token", tokens)
        self.assertIn("refresh_token", tokens)
        refreshed = auth_service.refresh_access_token(tokens["refresh_token"], self.db)
        self.assertEqual(refreshed["token_type"], "bearer")

        updated = auth_service.update_user(
            self.db,
            user,
            UserUpdate(full_name="Updated User", timezone="Africa/Lagos", default_currency="USD"),
        )
        self.assertEqual(updated.full_name, "Updated User")
        self.assertEqual(updated.timezone, "Africa/Lagos")
        self.assertEqual(updated.default_currency, "USD")

        auth_service.change_password(self.db, user, "password123", "newpassword123")
        self.assertTrue(auth_service.authenticate_user(
            self.db, UserLogin(email="new@example.com", password="newpassword123")
        ))

    def test_auth_rejects_duplicates_bad_password_inactive_and_bad_refresh_token(self):
        payload = UserRegister(email="dupe@example.com", password="password123", full_name="Dupe")
        auth_service.register_user(self.db, payload)

        with self.assertRaisesRegex(HTTPException, "400"):
            auth_service.register_user(self.db, payload)
        with self.assertRaisesRegex(HTTPException, "401"):
            auth_service.authenticate_user(
                self.db, UserLogin(email="dupe@example.com", password="wrongpassword")
            )
        with self.assertRaisesRegex(HTTPException, "401"):
            auth_service.refresh_access_token("not-a-token", self.db)

        inactive = auth_service.register_user(
            self.db,
            UserRegister(email="inactive@example.com", password="password123", full_name="Inactive"),
        )
        inactive.is_active = False
        self.db.commit()
        with self.assertRaisesRegex(HTTPException, "403"):
            auth_service.authenticate_user(
                self.db, UserLogin(email="inactive@example.com", password="password123")
            )

    def test_change_password_requires_current_password(self):
        user = auth_service.register_user(
            self.db,
            UserRegister(email="pw@example.com", password="password123", full_name="Password User"),
        )

        with self.assertRaisesRegex(HTTPException, "400"):
            auth_service.change_password(self.db, user, "wrongpassword", "newpassword123")


class ClientServiceTests(DatabaseTestCase):
    def test_create_update_list_stats_and_owner_scoping(self):
        client = client_service.create_client(
            self.db,
            ClientCreate(name="Acme Ltd", email="billing@acme.co"),
            self.user,
        )
        other_client = client_service.create_client(
            self.db,
            ClientCreate(name="Other Ltd", email="billing@other.co"),
            self.other_user,
        )
        self.create_invoice_row(
            self.user,
            invoice_number="INV-CLIENT-1",
            total=Decimal("125.50"),
            paid=Decimal("25.50"),
            client=client,
        )
        self.create_invoice_row(
            self.other_user,
            invoice_number="INV-OTHER-1",
            total=Decimal("999.00"),
            paid=Decimal("999.00"),
            client=other_client,
        )

        listed = client_service.list_clients_with_stats(self.db, self.user.id)
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["name"], "Acme Ltd")
        self.assertEqual(listed[0]["invoice_count"], 1)
        self.assertEqual(listed[0]["total_invoiced"], "125.50")
        self.assertEqual(listed[0]["total_paid"], "25.50")
        self.assertIsNone(client_service.get_client(self.db, other_client.id, self.user.id))

        updated = client_service.update_client(
            self.db,
            client,
            ClientUpdate(phone="+2348000000001", default_currency="USD"),
        )
        self.assertEqual(updated.phone, "+2348000000001")
        self.assertEqual(updated.default_currency, "USD")

        invoices = client_service.get_client_invoices(self.db, client.id, self.user.id)
        self.assertEqual([invoice.invoice_number for invoice in invoices], ["INV-CLIENT-1"])

    def test_get_client_or_404_raises_for_missing_client(self):
        with self.assertRaisesRegex(HTTPException, "404"):
            client_service.get_client_or_404(self.db, self.other_user.id, self.user.id)


class InvoiceStatusServiceTests(DatabaseTestCase):
    def test_status_transitions_record_history_and_timestamps(self):
        invoice = self.create_invoice_row(
            self.user,
            invoice_number="INV-STATUS-1",
            status=InvoiceStatus.DRAFT,
            total=Decimal("300.00"),
        )

        sent = mark_as_sent(self.db, invoice, changed_by=str(self.user.id))
        self.assertEqual(sent.status, InvoiceStatus.SENT)
        self.assertIsNotNone(sent.sent_at)

        viewed = mark_as_viewed(self.db, sent, changed_by=str(self.user.id))
        self.assertEqual(viewed.status, InvoiceStatus.VIEWED)
        self.assertIsNotNone(viewed.viewed_at)

        paid = mark_as_paid(self.db, viewed, changed_by=str(self.user.id), notes="Settled")
        self.assertEqual(paid.status, InvoiceStatus.PAID)
        self.assertEqual(paid.paid_amount, paid.total_amount)
        self.assertIsNotNone(paid.paid_at)

        history = get_status_history(self.db, paid.id)
        self.assertEqual([entry.status for entry in history], ["paid", "viewed", "sent"])
        self.assertEqual(history[0].notes, "Settled")

    def test_invalid_transition_and_terminal_cancelled_status_are_enforced(self):
        invoice = self.create_invoice_row(
            self.user,
            invoice_number="INV-STATUS-2",
            status=InvoiceStatus.DRAFT,
        )

        with self.assertRaisesRegex(HTTPException, "400"):
            transition_status(self.db, invoice, InvoiceStatus.PAID)

        cancelled = mark_as_cancelled(self.db, invoice, reason="Customer cancelled")
        self.assertEqual(cancelled.status, InvoiceStatus.CANCELLED)
        with self.assertRaisesRegex(HTTPException, "400"):
            transition_status(self.db, cancelled, InvoiceStatus.SENT)

    def test_check_and_mark_overdue_only_marks_due_active_invoices(self):
        overdue = self.create_invoice_row(
            self.user,
            invoice_number="INV-OVERDUE-1",
            status=InvoiceStatus.SENT,
            due_date=date.today() - timedelta(days=1),
        )
        paid = self.create_invoice_row(
            self.user,
            invoice_number="INV-OVERDUE-2",
            status=InvoiceStatus.PAID,
            due_date=date.today() - timedelta(days=1),
            paid=Decimal("100.00"),
        )

        self.assertTrue(check_and_mark_overdue(self.db, overdue))
        self.assertFalse(check_and_mark_overdue(self.db, paid))
        self.assertEqual(overdue.status, InvoiceStatus.OVERDUE)
        self.assertEqual(paid.status, InvoiceStatus.PAID)


class PaymentServiceTests(DatabaseTestCase):
    def test_create_partial_and_full_payments_update_invoice_and_summary(self):
        invoice = self.create_invoice_row(
            self.user,
            invoice_number="INV-PAY-1",
            status=InvoiceStatus.SENT,
            total=Decimal("100.00"),
        )

        partial = create_payment(
            self.db,
            PaymentCreate(invoice_id=invoice.id, amount=Decimal("40.00"), reference_number="REF-1"),
            self.user,
        )
        self.assertEqual(partial.amount, Decimal("40.00"))
        self.assertEqual(invoice.paid_amount, Decimal("40.00"))
        self.assertEqual(invoice.status, InvoiceStatus.PARTIAL)

        full = create_payment(
            self.db,
            PaymentCreate(invoice_id=invoice.id, amount=Decimal("60.00"), reference_number="REF-2"),
            self.user,
        )
        self.assertEqual(full.amount, Decimal("60.00"))
        self.assertEqual(invoice.paid_amount, Decimal("100.00"))
        self.assertEqual(invoice.status, InvoiceStatus.PAID)

        summary = get_payment_summary(self.db, self.user.id)
        self.assertEqual(summary, {"total_payments": 2, "total_amount": 100.0})

    def test_create_payment_rejects_overpayment_and_non_owner_invoice(self):
        invoice = self.create_invoice_row(
            self.user,
            invoice_number="INV-PAY-2",
            status=InvoiceStatus.SENT,
            total=Decimal("100.00"),
        )
        other_invoice = self.create_invoice_row(
            self.other_user,
            invoice_number="INV-PAY-OTHER",
            status=InvoiceStatus.SENT,
            total=Decimal("100.00"),
        )

        with self.assertRaisesRegex(HTTPException, "400"):
            create_payment(
                self.db,
                PaymentCreate(invoice_id=invoice.id, amount=Decimal("100.01")),
                self.user,
            )
        with self.assertRaisesRegex(HTTPException, "404"):
            create_payment(
                self.db,
                PaymentCreate(invoice_id=other_invoice.id, amount=Decimal("1.00")),
                self.user,
            )

    def test_update_and_delete_payment_recalculate_invoice_status(self):
        invoice = self.create_invoice_row(
            self.user,
            invoice_number="INV-PAY-3",
            status=InvoiceStatus.SENT,
            total=Decimal("100.00"),
        )
        payment = create_payment(
            self.db,
            PaymentCreate(invoice_id=invoice.id, amount=Decimal("30.00")),
            self.user,
        )

        updated = update_payment(
            self.db,
            payment,
            PaymentUpdate(amount=Decimal("100.00"), notes="Corrected"),
            self.user,
        )
        self.assertEqual(updated.amount, Decimal("100.00"))
        self.assertEqual(invoice.paid_amount, Decimal("100.00"))
        self.assertEqual(invoice.status, InvoiceStatus.PAID)

        delete_payment(self.db, updated, self.user)
        self.assertEqual(invoice.paid_amount, Decimal("0.00"))
        self.assertEqual(invoice.status, InvoiceStatus.SENT)


class DashboardServiceTests(DatabaseTestCase):
    def test_metrics_are_user_scoped_and_include_status_activity_overdue_and_revenue(self):
        today = date.today()
        overdue_invoice = self.create_invoice_row(
            self.user,
            invoice_number="INV-DASH-OVERDUE",
            status=InvoiceStatus.SENT,
            total=Decimal("200.00"),
            paid=Decimal("50.00"),
            due_date=today - timedelta(days=3),
            created_at=datetime(2026, 5, 21, 10, 0, 0),
        )
        paid_invoice = self.create_invoice_row(
            self.user,
            invoice_number="INV-DASH-PAID",
            status=InvoiceStatus.PAID,
            total=Decimal("300.00"),
            paid=Decimal("300.00"),
            due_date=today + timedelta(days=10),
            created_at=datetime(2026, 5, 22, 10, 0, 0),
        )
        self.create_invoice_row(
            self.other_user,
            invoice_number="INV-DASH-OTHER",
            status=InvoiceStatus.PAID,
            total=Decimal("900.00"),
            paid=Decimal("900.00"),
        )
        self.create_payment_row(paid_invoice, "300.00", payment_date=today - timedelta(days=2))
        self.create_payment_row(overdue_invoice, "50.00", payment_date=today - timedelta(days=40))

        metrics = dashboard_service.get_dashboard_metrics(self.db, self.user.id)

        self.assertEqual(metrics["summary"]["total_invoiced"], 500.0)
        self.assertEqual(metrics["summary"]["total_paid"], 350.0)
        self.assertEqual(metrics["summary"]["outstanding"], 150.0)
        self.assertEqual(metrics["summary"]["overdue_amount"], 150.0)
        self.assertEqual(metrics["summary"]["total_invoices"], 2)
        self.assertEqual(metrics["recent_activity"]["payments_count"], 1)
        self.assertEqual(metrics["recent_activity"]["payments_total"], 300.0)
        self.assertEqual(metrics["status_breakdown"]["sent"]["count"], 1)
        self.assertEqual(metrics["status_breakdown"]["paid"]["total"], 300.0)
        self.assertEqual(metrics["overdue"]["invoices"][0]["invoice_number"], "INV-DASH-OVERDUE")
        self.assertIn({"month": today.strftime("%Y-%m"), "revenue": 300.0}, metrics["monthly_revenue"])

    def test_recent_activity_combines_invoices_and_payments_in_descending_order(self):
        older_invoice = self.create_invoice_row(
            self.user,
            invoice_number="INV-ACT-OLD",
            status=InvoiceStatus.SENT,
            total=Decimal("100.00"),
            created_at=datetime(2026, 5, 20, 9, 0, 0),
        )
        newer_invoice = self.create_invoice_row(
            self.user,
            invoice_number="INV-ACT-NEW",
            status=InvoiceStatus.SENT,
            total=Decimal("200.00"),
            created_at=datetime(2026, 5, 22, 9, 0, 0),
        )
        self.create_payment_row(older_invoice, "20.00", payment_date=date(2026, 5, 21))
        self.create_payment_row(newer_invoice, "30.00", payment_date=date(2026, 5, 23))

        activity = dashboard_service.get_recent_activity(self.db, self.user.id, limit=3)

        self.assertEqual(len(activity), 3)
        self.assertEqual(activity[0]["type"], "payment_received")
        self.assertEqual(activity[0]["description"], "Payment received for INV-ACT-NEW")
        self.assertEqual(activity[1]["description"], "Invoice INV-ACT-NEW created for Ada Client")
        self.assertEqual(activity[2]["description"], "Payment received for INV-ACT-OLD")

    def test_upcoming_invoices_excludes_paid_cancelled_overdue_and_other_users(self):
        today = date.today()
        due_soon = self.create_invoice_row(
            self.user,
            invoice_number="INV-UPCOMING-1",
            status=InvoiceStatus.SENT,
            total=Decimal("100.00"),
            due_date=today + timedelta(days=2),
        )
        self.create_invoice_row(
            self.user,
            invoice_number="INV-UPCOMING-PAID",
            status=InvoiceStatus.PAID,
            total=Decimal("100.00"),
            paid=Decimal("100.00"),
            due_date=today + timedelta(days=1),
        )
        self.create_invoice_row(
            self.user,
            invoice_number="INV-UPCOMING-LATE",
            status=InvoiceStatus.SENT,
            total=Decimal("100.00"),
            due_date=today - timedelta(days=1),
        )
        self.create_invoice_row(
            self.other_user,
            invoice_number="INV-UPCOMING-OTHER",
            status=InvoiceStatus.SENT,
            total=Decimal("100.00"),
            due_date=today + timedelta(days=1),
        )

        upcoming = dashboard_service.get_upcoming_invoices(self.db, self.user.id, days=7)

        self.assertEqual(len(upcoming), 1)
        self.assertEqual(upcoming[0]["id"], str(due_soon.id))
        self.assertEqual(upcoming[0]["days_until_due"], 2)


class InvoiceCreateTests(DatabaseTestCase):
    def test_create_invoice_calculates_totals_and_rejects_duplicate_numbers_per_user(self):
        payload = InvoiceCreate(
            invoice_number="INV-CREATE-1",
            issuer_email="owner@example.com",
            customer_name="Ada Client",
            customer_email="ada@example.com",
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            currency="usd",
            tax_rate=Decimal("7.50"),
            items=[
                InvoiceItemCreate(description="Design", quantity=2, unit_price=Decimal("10.005")),
                InvoiceItemCreate(description="Support", quantity=1, unit_price=Decimal("5.00")),
            ],
        )

        invoice = create_invoice(self.db, payload, self.user)

        self.assertEqual(invoice.currency, "USD")
        self.assertEqual(invoice.issuer_name, self.user.full_name)
        self.assertEqual(invoice.subtotal, Decimal("25.01"))
        self.assertEqual(invoice.tax_amount, Decimal("1.88"))
        self.assertEqual(invoice.total_amount, Decimal("26.89"))

        with self.assertRaisesRegex(HTTPException, "409"):
            create_invoice(self.db, payload, self.user)

        other_invoice = create_invoice(self.db, payload, self.other_user)
        self.assertEqual(other_invoice.invoice_number, "INV-CREATE-1")

    def test_update_invoice_edits_metadata_and_recalculates_tax_total(self):
        invoice = self.create_invoice_row(
            self.user,
            invoice_number="INV-UPDATE-1",
            total=Decimal("100.00"),
        )

        updated = update_invoice(
            self.db,
            invoice,
            InvoiceUpdate(
                invoice_number="INV-UPDATE-2",
                customer_name="Updated Customer",
                currency="usd",
                tax_rate=Decimal("7.50"),
            ),
        )

        self.assertEqual(updated.invoice_number, "INV-UPDATE-2")
        self.assertEqual(updated.customer_name, "Updated Customer")
        self.assertEqual(updated.currency, "USD")
        self.assertEqual(updated.tax_amount, Decimal("7.50"))
        self.assertEqual(updated.total_amount, Decimal("107.50"))


class ExportAndUploadScopeTests(DatabaseTestCase):
    def test_generate_pdf_rejects_invoice_owned_by_another_user(self):
        invoice = self.create_invoice_row(self.other_user, invoice_number="INV-EXPORT-OTHER")

        with self.assertRaises(HTTPException) as raised:
            generate_pdf(self.db, str(invoice.id), self.user.id)

        self.assertEqual(raised.exception.status_code, 404)

    def test_save_logo_rejects_invoice_owned_by_another_user_before_writing_file(self):
        class Upload:
            content_type = "image/png"
            filename = "logo.png"

            async def read(self):
                return b"not really a png"

        invoice = self.create_invoice_row(self.other_user, invoice_number="INV-LOGO-OTHER")

        with tempfile.TemporaryDirectory() as tmpdir:
            from app.core.config import settings

            original_logos_dir = settings.logos_dir
            settings.logos_dir = tmpdir
            try:
                with self.assertRaises(HTTPException) as raised:
                    asyncio.run(save_logo_for_invoice(self.db, str(invoice.id), Upload(), self.user.id))
            finally:
                settings.logos_dir = original_logos_dir

            self.assertEqual(raised.exception.status_code, 404)
            self.assertEqual(os.listdir(tmpdir), [])


if __name__ == "__main__":
    unittest.main()
