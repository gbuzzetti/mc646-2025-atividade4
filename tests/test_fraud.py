import pytest
from datetime import datetime, timedelta
from src.fraud.Transaction import Transaction
from src.fraud.FraudDetectionSystem import FraudDetectionSystem
from src.fraud.FraudCheckResult import FraudCheckResult

class TestFraudDetectionSystem:
    def setup_method(self):
        self.system = FraudDetectionSystem()

    def test_normal_transaction(self):
        current_transaction = Transaction(500, datetime.now(), "Brasil")
        previous_transactions = []
        blacklisted_locations = []
        result = self.system.check_for_fraud(current_transaction, previous_transactions, blacklisted_locations)
        assert result.is_fraudulent == False
        assert result.is_blocked == False
        assert result.verification_required == False
        assert result.risk_score == 0

    def test_less_than_10_transactions(self):
        now = datetime.now()
        current_transaction = Transaction(100, now, "Brasil")
        previous_transactions = [Transaction(100, now - timedelta(minutes=30), "Brasil") for _ in range(5)]
        blacklisted_locations = []
        result = self.system.check_for_fraud(current_transaction, previous_transactions, blacklisted_locations)
        assert result.is_blocked == False
        assert result.risk_score == 0

    def test_high_amount(self):
        # Regra 1: Transação com valor acima de 10000 deve ser marcada como fraudulenta e requerer verificação
        current_transaction = Transaction(15000, datetime.now(), "Brasil")
        previous_transactions = []
        blacklisted_locations = []
        result = self.system.check_for_fraud(current_transaction, previous_transactions, blacklisted_locations)
        assert result.is_fraudulent == True
        assert result.verification_required == True
        assert result.risk_score == 50

    def test_excessive_transactions(self):
        # Regra 2: Mais de 10 transações na última hora deve bloquear o cartão
        now = datetime.now()
        current_transaction = Transaction(100, now, "Brasil")
        previous_transactions = [Transaction(100, now - timedelta(minutes=30), "Brasil") for _ in range(11)]
        blacklisted_locations = []
        result = self.system.check_for_fraud(current_transaction, previous_transactions, blacklisted_locations)
        assert result.is_blocked == True
        assert result.risk_score == 30

    def test_location_change(self):
        # Regra 3: Mudança de localização em menos de 30 minutos
        now = datetime.now()
        current_transaction = Transaction(100, now, "EUA")
        previous_transactions = [Transaction(100, now - timedelta(minutes=20), "Brasil")]
        blacklisted_locations = []
        result = self.system.check_for_fraud(current_transaction, previous_transactions, blacklisted_locations)
        assert result.is_fraudulent == True
        assert result.verification_required == True
        assert result.risk_score == 20

    def test_blacklisted_location(self):
        # Regra 4: Localização na blacklist
        current_transaction = Transaction(100, datetime.now(), "País de Alto Risco")
        previous_transactions = []
        blacklisted_locations = ["País de Alto Risco"]
        result = self.system.check_for_fraud(current_transaction, previous_transactions, blacklisted_locations)
        assert result.is_blocked == True
        assert result.risk_score == 100

    def test_combined_rules(self):
        # Teste com múltiplas regras ativas
        now = datetime.now()
        current_transaction = Transaction(15000, now, "País de Alto Risco")
        previous_transactions = [Transaction(100, now - timedelta(minutes=20), "Brasil") for _ in range(11)]
        blacklisted_locations = ["País de Alto Risco"]
        result = self.system.check_for_fraud(current_transaction, previous_transactions, blacklisted_locations)
        assert result.is_blocked == True
        assert result.risk_score == 100
