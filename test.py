import os
import unittest
from bank import BankInterface, Transaction
from datetime import datetime


class TestBankInterface(unittest.TestCase):
    def setUp(self):
        self.bank_interface = BankInterface()
        self.bank_interface.create_account("test_account", "Debit", "USD")

    def tearDown(self):
        del self.bank_interface.accounts["test_account"]
        file_to_delete = "bank_data.json"
        if os.path.exists(file_to_delete):
            os.remove(file_to_delete)

    def test_import_transactions_and_get_balance(self):
        # Create and import transactions
        transactions = [
            Transaction(datetime(2023, 11, 1), "Salary", 500, "USD"),
            Transaction(datetime(2023, 11, 5), "Rent", -200, "USD"),
            Transaction(datetime(2023, 11, 10), "Groceries", -50, "USD"),
        ]
        self.bank_interface.import_transactions_to_account("test_account", transactions)

        # Get current balance
        self.assertEqual(self.bank_interface.accounts["test_account"].balance, 250)

    def test_get_balance_on_specific_date(self):
        # Import transactions with different dates
        transactions = [
            Transaction(datetime(2023, 11, 1), "Salary", 500, "USD"),
            Transaction(datetime(2023, 11, 5), "Rent", -200, "USD"),
        ]
        self.bank_interface.import_transactions_to_account("test_account", transactions)

        # Get balance on a specific date
        specific_date = datetime(2023, 11, 3)
        balance = self.bank_interface.accounts["test_account"].get_balance_at_date(specific_date)
        self.assertEqual(balance, 500)  # Should be the balance after salary but before rent


if __name__ == '__main__':
    unittest.main()
