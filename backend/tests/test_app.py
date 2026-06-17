import os
import unittest

os.environ["DEBUG"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret"


class AppImportTests(unittest.TestCase):
    def test_app_imports_and_health_check_responds(self):
        from app.main import health_check

        self.assertEqual(health_check(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
