import unittest
import sqlite3
import tempfile
import os
import database
from unittest.mock import patch
from bakery_calculator import pay_with_cash


from database import add_payment


class TestPayments(unittest.TestCase):

    @patch("builtins.input", return_value="500")
    def test_cash_overpayment_returns_change(self, mock_input):
        result = pay_with_cash(400)

        self.assertEqual(result[0], "Cash")
        self.assertEqual(result[3], 100)
        self.assertEqual(result[4], 400)

    def setUp(self):
        # Create a temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        # Create orders table
        cursor.execute("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                total INTEGER,
                amount_paid INTEGER,
                payment_status TEXT
            )
        """)

        # Create payments table
        cursor.execute("""
            CREATE TABLE payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                amount INTEGER,
                payment_method TEXT,
                reference TEXT,
                payment_date TEXT
            )
        """)
        # Create order_items table
        cursor.execute("""
            CREATE TABLE order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                product_name TEXT,
                quantity INTEGER,
                unit_price INTEGER
            )
        """)

        # Create a test order
        cursor.execute("""
            INSERT INTO orders
            VALUES (1, 1000, 400, 'PARTIALLY PAID')
        """)

        connection.commit()
        connection.close()

    def tearDown(self):
        os.remove(self.db_path)



    def test_successful_payment(self):
        result = add_payment(
            1,
            600,
            "Bank Transfer",
            "TEST123",
            "2026-11-12",
            self.db_path
        )

        self.assertTrue(result)

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT amount_paid, payment_status FROM orders WHERE id = 1"
        )

        order = cursor.fetchone()
        connection.close()

        self.assertEqual(order[0], 1000)
        self.assertEqual(order[1], "PAID")

    def test_rejects_excessive_payment(self):
        result = add_payment(
            1,
            700,
            "Cash",
            None,
            "2026-11-12",
            self.db_path
        )

        self.assertFalse(result)

    def test_rejects_zero_payment(self):
        result = add_payment(
            1, 0, "Cash", None, "2026-11-12", self.db_path
        )

        self.assertFalse(result)

    def test_rejects_negative_payment(self):
        result = add_payment(
            1, -200, "Cash", None, "2026-11-12", self.db_path
        )

        self.assertFalse(result)

    def test_rejects_nonexistent_order(self):
        result = add_payment(
            999,
            500,
            "Cash",
            None,
            "2026-11-12",
            self.db_path
        )

        self.assertFalse(result)

    def test_payment_is_saved_in_history(self):
        add_payment(
            1,
            200,
            "Cash",
            None,
            "2026-11-12",
            self.db_path
        )

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT amount, payment_method FROM payments WHERE order_id = 1"
        )

        payment = cursor.fetchone()
        connection.close()

        self.assertEqual(payment[0], 200)
        self.assertEqual(payment[1], "Cash")

    def test_partial_payment_status(self):
        result = add_payment(
            1,
            200,
            "Cash",
            None,
            "2026-11-12",
            self.db_path
        )

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT amount_paid, payment_status FROM orders WHERE id = 1"
        )

        order = cursor.fetchone()
        connection.close()

        self.assertTrue(result)
        self.assertEqual(order[0], 600)
        self.assertEqual(order[1], "PARTIALLY PAID")


    def test_rejects_payment_on_fully_paid_order(self):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE orders
            SET amount_paid = 1000, payment_status = 'PAID'
            WHERE id = 1
        """)

        connection.commit()
        connection.close()

        result = add_payment(
            1,
            100,
            "Cash",
            None,
            "2026-11-12",
            self.db_path
        )

        self.assertFalse(result)

    def test_rejected_payment_does_not_change_balance(self):
        result = add_payment(
            1,
            700,
            "Cash",
            None,
            "2026-11-12",
            self.db_path
        )

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT amount_paid FROM orders WHERE id = 1"
        )

        amount_paid = cursor.fetchone()[0]
        connection.close()

        self.assertFalse(result)
        self.assertEqual(amount_paid, 400)

    def test_multiple_instalments(self):
        first_payment = add_payment(
            1, 200, "Cash", None, "2026-11-12", self.db_path
        )

        second_payment = add_payment(
            1, 400, "Bank Transfer", "TRF123",
            "2026-11-12", self.db_path
        )

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT amount_paid, payment_status FROM orders WHERE id = 1"
        )

        order = cursor.fetchone()

        cursor.execute(
            "SELECT COUNT(*) FROM payments WHERE order_id = 1"
        )

        payment_count = cursor.fetchone()[0]
        connection.close()

        self.assertTrue(first_payment)
        self.assertTrue(second_payment)
        self.assertEqual(order[0], 1000)
        self.assertEqual(order[1], "PAID")
        self.assertEqual(payment_count, 2)

    def test_multiple_payments_saved_in_history(self):
        add_payment(
            1, 200, "Cash", None, "2026-11-12", self.db_path
        )

        add_payment(
            1, 400, "Bank Transfer", "TRF123",
            "2026-11-12", self.db_path
        )

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT amount, payment_method
            FROM payments
            WHERE order_id = 1
            ORDER BY id
        """)

        payments = cursor.fetchall()
        connection.close()

        self.assertEqual(len(payments), 2)
        self.assertEqual(payments[0], (200, "Cash"))
        self.assertEqual(payments[1], (400, "Bank Transfer"))

    def test_rejected_payment_not_saved_in_history(self):
        result = add_payment(
            1,
            700,
            "Cash",
            None,
            "2026-11-12",
            self.db_path
        )

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM payments WHERE order_id = 1"
        )

        payment_count = cursor.fetchone()[0]
        connection.close()

        self.assertFalse(result)
        self.assertEqual(payment_count, 0)

    @patch("builtins.input", return_value="0")
    def test_unpaid_order(self, mock_input):
        result = pay_with_cash(400)

        self.assertEqual(result[0], "Cash")
        self.assertEqual(result[1], "UNPAID")
        self.assertEqual(result[3], 0)
        self.assertEqual(result[4], 0)
    def test_editing_order_preserves_payment_history(self):
        original_database = database.DATABASE
        database.DATABASE = self.db_path

        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO payments
                (order_id, amount, payment_method, reference, payment_date)
                VALUES (1, 400, 'Cash', NULL, '2026-11-19')
            """)

            connection.commit()
            connection.close()

            result = database.update_order_items(
                1,
                1500,
                [("Chocolate Cake", 1500, 1)]
            )

            self.assertTrue(result)

            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()

            cursor.execute("""
                SELECT amount, payment_method
                FROM payments WHERE order_id = 1
            """)

            payment = cursor.fetchone()

            cursor.execute("""
                SELECT total, amount_paid, payment_status
                FROM orders WHERE id = 1
            """)

            order = cursor.fetchone()
            connection.close()

            self.assertEqual(payment, (400, "Cash"))
            self.assertEqual(order, (1500, 400, "PARTIALLY PAID"))

        finally:
            database.DATABASE = original_database

    def test_rejects_order_total_below_amount_paid(self):
        original_database = database.DATABASE
        database.DATABASE = self.db_path

        try:
            result = database.update_order_items(
                1,
                300,
                [("Buns", 300, 1)]
            )

            self.assertFalse(result)

        finally:
            database.DATABASE = original_database
