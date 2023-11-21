import json
from datetime import datetime

CURRENCT_RATES = {}


class Transaction:
    def __init__(self, date, description, amount, currency):
        self.date = date
        self.description = description
        self.amount = amount
        self.currency = currency


class BankAccount:
    def __init__(self, account_type, currency, credit_limit=None):
        self.account_type = account_type
        self.currency = currency
        self.credit_limit = credit_limit
        self.transactions = []
        self.balance = 0

    def import_transactions(self, transactions):
        for transaction in transactions:
            self.add_transaction(transaction)

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        self.update_balance()

    def update_balance(self):
        self.balance = 0
        for transaction in self.transactions:
            if transaction.currency != self.currency:
                converted_amount = self.convert_currency(transaction.amount, transaction.currency, self.currency, transaction.date)
                self.balance += converted_amount
            else:
                self.balance += transaction.amount

        if self.account_type == 'Debit' and self.balance < 0:
            print("Cannot have negative balance in Debit account.")
            self.transactions.pop()
            self.update_balance()

        if self.account_type == 'Credit' and self.balance < -self.credit_limit:
            print("Credit limit exceeded.")
            self.transactions.pop()
            self.update_balance()

    def convert_currency(self, amount, from_currency, to_currency, date):
        global CURRENCT_RATES
        if from_currency == to_currency:
            return amount

        if from_currency in CURRENCT_RATES and to_currency in CURRENCT_RATES[from_currency]:
            rate_info = CURRENCT_RATES[from_currency][to_currency]
            if date >= datetime.strptime(rate_info['date'], '%Y-%m-%d'):
                converted_amount = amount * rate_info['rate']
                return converted_amount
            else:
                raise Exception("Currency rates for conversion date not available.")
        else:
            raise Exception("Currency conversion rate not available.")

    def get_balance_at_date(self, date):
        balance_at_date = 0
        for transaction in self.transactions:
            if transaction.date <= date:
                balance_at_date += transaction.amount
        return balance_at_date

    def get_transactions_in_range(self, start_date, end_date):
        transactions_in_range = []
        for transaction in self.transactions:
            if start_date <= transaction.date <= end_date:
                transactions_in_range.append(transaction)
        return transactions_in_range


class BankInterface:
    global CURRENCT_RATES
    def __init__(self):
        self.accounts = {}
        self.load_from_file("bank_data.json")
        self.load_currency_rates("currency_rates.json")

    def create_account(self, account_name, account_type, currency, credit_limit=None):
        self.accounts[account_name] = BankAccount(account_type, currency, credit_limit)
        self.save_to_file("bank_data.json")

    def create_currency_rate(self, base_currency, target_currency, rate, date):
        if base_currency not in CURRENCT_RATES:
            CURRENCT_RATES[base_currency] = {}
        CURRENCT_RATES[base_currency][target_currency] = {'rate': rate, 'date': date}
        self.save_currency_rates("currency_rates.json")

    def save_currency_rates(self, file_name):
        try:
            with open(file_name, 'w') as file:
                json.dump(CURRENCT_RATES, file, indent=4)
            print("Currency rates saved successfully.")
        except Exception as e:
            print(f"Error saving currency rates: {str(e)}")

    def load_currency_rates(self, file_name):
        global CURRENCT_RATES
        try:
            with open(file_name, 'r') as file:
                CURRENCT_RATES = json.load(file)
            print("Currency rates loaded successfully.")
        except FileNotFoundError:
            print("Currency rates file not found. Initializing with empty rates.")
            CURRENCT_RATES = {}
        except Exception as e:
            print(f"Error loading currency rates: {str(e)}")

    def import_transactions_to_account(self, account_name, transactions):
        if account_name in self.accounts:
            self.accounts[account_name].import_transactions(transactions)
            self.save_to_file("bank_data.json")
        else:
            print("Account not found.")

    def create_transaction(self, account_name, date, description, amount, currency):
        if account_name in self.accounts:
            transaction = Transaction(date, description, amount, currency)
            self.accounts[account_name].add_transaction(transaction)
            self.save_to_file("bank_data.json")
            print("Transaction added successfully.")
        else:
            print("Account not found.")

    def import_transactions_from_csv(self, account_name, file_name):
        try:
            with open(file_name, 'r') as file:
                csv_reader = csv.DictReader(file)
                transactions = [
                    Transaction(
                        date=datetime.strptime(row['Date'], '%Y-%m-%d'),
                        description=row['Description'],
                        amount=float(row['Amount']),
                        currency=row['Currency']
                    )
                    for row in csv_reader
                ]
                self.import_transactions_to_account(account_name, transactions)
                print("Transactions imported successfully.")
        except FileNotFoundError:
            print("File not found.")
        except Exception as e:
            print(f"Error importing transactions: {str(e)}")

    def display_balance(self, account_name):
        if account_name in self.accounts:
            print(f"Current balance for {account_name}: {self.accounts[account_name].balance} {self.accounts[account_name].currency}")
        else:
            print("Account not found.")

    def display_menu(self):
        print("Bank Application Menu:")
        print("1. Create Account")
        print("2. Import Transactions from CSV")
        print("3. Display Balance")
        print("4. Get Balance at Date")
        print("5. Get Transactions in Range")
        print("6. Create Transaction")
        print("7. Add Currency")
        print("8. Exit")

    def run_menu(self):
        while True:
            self.display_menu()
            choice = input("Enter your choice: ")

            if choice == '1':
                account_name = input("Enter account name: ")
                account_type = input("Enter account type (Debit/Credit): ")
                currency = input("Enter currency: ")
                credit_limit = float(input("Enter credit limit (if applicable, else press Enter): ") or 0)
                self.create_account(account_name, account_type, currency, credit_limit)

            elif choice == '2':
                account_name = input("Enter account name to import transactions: ")
                file_name = input("Enter CSV file name: ")
                self.import_transactions_from_csv(account_name, file_name)
                print("Functionality to import transactions from CSV not implemented.")

            elif choice == '3':
                account_name = input("Enter account name to display balance: ")
                self.display_balance(account_name)

            elif choice == '4':
                account_name = input("Enter account name: ")
                date_str = input("Enter date in YYYY-MM-DD format: ")
                date = datetime.strptime(date_str, '%Y-%m-%d')
                self.get_balance_at_date(account_name, date)

            elif choice == '5':
                account_name = input("Enter account name: ")
                start_date_str = input("Enter start date in YYYY-MM-DD format: ")
                end_date_str = input("Enter end date in YYYY-MM-DD format: ")
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                self.get_transactions_in_range(account_name, start_date, end_date)

            elif choice == '6':
                account_name = input("Enter account name: ")
                date_str = input("Enter date in YYYY-MM-DD format: ")
                date = datetime.strptime(date_str, '%Y-%m-%d')
                description = input("Enter description: ")
                amount = float(input("Enter amount: "))
                currency = input("Enter currency: ")
                self.create_transaction(account_name, date, description, amount, currency)

            elif choice == '7':
                base_currency = input("Enter base currency: ")
                target_currency = input("Enter target currency: ")
                rate = float(input("Enter exchange rate: "))
                date = input("Enter rate date (YYYY-MM-DD): ")

                self.create_currency_rate(base_currency, target_currency, rate, date)
            elif choice == '8':
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please enter a valid option.")

    def save_to_file(self, file_name):
        data = {
            'accounts': {name: {
                'account_type': account.account_type,
                'currency': account.currency,
                'credit_limit': account.credit_limit,
                'transactions': [
                    {
                        'date': transaction.date.strftime('%Y-%m-%d'),
                        'description': transaction.description,
                        'amount': transaction.amount,
                        'currency': transaction.currency
                    }
                    for transaction in account.transactions
                ]
            } for name, account in self.accounts.items()}
        }

        try:
            with open(file_name, 'w') as file:
                json.dump(data, file, indent=4)
            print("Data saved successfully.")
        except Exception as e:
            print(f"Error saving data: {str(e)}")

    def load_from_file(self, file_name):
        try:
            with open(file_name, 'r') as file:
                data = json.load(file)
                for account_name, account_data in data['accounts'].items():
                    account = BankAccount(
                        account_type=account_data['account_type'],
                        currency=account_data['currency'],
                        credit_limit=account_data['credit_limit']
                    )
                    transactions = [
                        Transaction(
                            date=datetime.strptime(trans['date'], '%Y-%m-%d'),
                            description=trans['description'],
                            amount=trans['amount'],
                            currency=trans['currency']
                        )
                        for trans in account_data['transactions']
                    ]
                    account.import_transactions(transactions)
                    self.accounts[account_name] = account
            print("Data loaded successfully.")
        except Exception as e:
            print(f"Error loading data: {str(e)}")

    def get_balance_at_date(self, account_name, date):
        if account_name in self.accounts:
            balance = self.accounts[account_name].get_balance_at_date(date)
            print(f"Balance for {account_name} at {date}: {balance} {self.accounts[account_name].currency}")
        else:
            print("Account not found.")

    def get_transactions_in_range(self, account_name, start_date, end_date):
        if account_name in self.accounts:
            transactions = self.accounts[account_name].get_transactions_in_range(start_date, end_date)
            print(f"Transactions for {account_name} between {start_date} and {end_date}:")
            for transaction in transactions:
                print(f"{transaction.date.strftime('%Y-%m-%d')}: {transaction.description} - {transaction.amount} {transaction.currency}")
        else:
            print("Account not found.")


def main():
    bank_interface = BankInterface()
    bank_interface.run_menu()


if __name__ == "__main__":
    main()
