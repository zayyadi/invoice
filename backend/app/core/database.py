from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def _repair_existing_schema() -> None:
    """Bring older local databases up to the columns the current app expects."""
    statements = [
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS user_id UUID",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS client_id UUID",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'DRAFT'",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS issuer_name VARCHAR(255)",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS issuer_email VARCHAR(255)",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS issuer_phone VARCHAR(50)",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS issuer_address TEXT",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS payment_bank_name VARCHAR(255)",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS payment_account_number VARCHAR(50)",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS payment_account_name VARCHAR(255)",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS sent_at TIMESTAMP",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS viewed_at TIMESTAMP",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS paid_at TIMESTAMP",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS currency VARCHAR(3) DEFAULT 'NGN'",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS tax_rate NUMERIC(5, 2) DEFAULT 0",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS subtotal NUMERIC(12, 2) DEFAULT 0",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS tax_amount NUMERIC(12, 2) DEFAULT 0",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS total_amount NUMERIC(12, 2) DEFAULT 0",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS paid_amount NUMERIC(12, 2) DEFAULT 0",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS notes TEXT",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS logo_path VARCHAR(500)",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "ALTER TABLE invoices ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "ALTER TABLE invoice_items ADD COLUMN IF NOT EXISTS line_total NUMERIC(12, 2) DEFAULT 0",
        "ALTER TABLE clients ADD COLUMN IF NOT EXISTS user_id UUID",
        "ALTER TABLE clients ADD COLUMN IF NOT EXISTS phone VARCHAR(50)",
        "ALTER TABLE clients ADD COLUMN IF NOT EXISTS address TEXT",
        "ALTER TABLE clients ADD COLUMN IF NOT EXISTS tax_id VARCHAR(100)",
        "ALTER TABLE clients ADD COLUMN IF NOT EXISTS notes TEXT",
        "ALTER TABLE clients ADD COLUMN IF NOT EXISTS default_currency VARCHAR(3)",
        "ALTER TABLE clients ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "ALTER TABLE payments ADD COLUMN IF NOT EXISTS user_id UUID",
        "ALTER TABLE payments ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "CREATE INDEX IF NOT EXISTS ix_invoices_user_id ON invoices (user_id)",
        "CREATE INDEX IF NOT EXISTS ix_invoices_client_id ON invoices (client_id)",
        "CREATE INDEX IF NOT EXISTS ix_clients_user_id ON clients (user_id)",
        "CREATE INDEX IF NOT EXISTS ix_payments_user_id ON payments (user_id)",
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def ensure_database_schema() -> None:
    import app.models.client  # noqa: F401
    import app.models.invoice  # noqa: F401
    import app.models.invoice_status_history  # noqa: F401
    import app.models.payment  # noqa: F401
    import app.models.user  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _repair_existing_schema()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
