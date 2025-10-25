import pytest
from datetime import datetime, timedelta
from fraud.Transaction import Transaction
from fraud.FraudDetectionSystem import FraudDetectionSystem
from fraud.FraudCheckResult import FraudCheckResult

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

    # Novos testes após a primeira análise dos resultados do mutmut

    def test_high_amount_at_boundary(self):
        # Mata os mutantes 144 (> para >=) e 145 (> para > 10001)
        
        # Teste 1: Exatamente no limite
        current_transaction = Transaction(10000, datetime.now(), "Brasil")
        result = self.system.check_for_fraud(current_transaction, [], [])
        # Original (>) deve ser Falso
        assert result.is_fraudulent == False, "Falha no limite 10000"

        # Teste 2: Imediatamente acima do limite
        current_transaction = Transaction(10001, datetime.now(), "Brasil")
        result = self.system.check_for_fraud(current_transaction, [], [])
        # Original (>) deve ser Verdadeiro
        assert result.is_fraudulent == True, "Falha no limite 10001"

    def test_excessive_transactions_at_boundary(self):
        # Mata o mutante 165 (> 10 para >= 10)
        now = datetime.now()
        # Exatamente 10 transações anteriores (total 11)
        previous_transactions = [Transaction(100, now - timedelta(minutes=30), "Brasil") for _ in range(10)]
        current_transaction = Transaction(100, now, "Brasil")
        
        result = self.system.check_for_fraud(current_transaction, previous_transactions, [])
        # Original (> 10) deve ser Falso
        assert result.is_blocked == False, "Contagem de 10 não deve bloquear"

    def test_time_boundaries_for_transactions(self):
        # Mata o mutante 160 (<= 60 para < 60)
        now = datetime.now()
        # 10 transações no limite exato de 60 minutos
        previous_transactions = [Transaction(100, now - timedelta(minutes=60), "Brasil") for _ in range(10)]
        current_transaction = Transaction(100, now, "Brasil")
        
        result = self.system.check_for_fraud(current_transaction, previous_transactions, [])
        # Original (<= 60) deve contar 10 e não bloquear
        assert result.is_blocked == False, "Não deve bloquear com tx @ 60min"

    def test_location_change_operator_mutation(self):
        # Mata o mutante 183 (and para or)
        now = datetime.now()
        
        # Cenário: Tempo está FORA do limite (False), mas Localização é diferente (True)
        current_transaction = Transaction(100, now, "EUA")
        previous_transactions = [Transaction(100, now - timedelta(minutes=40), "Brasil")]
        
        result = self.system.check_for_fraud(current_transaction, previous_transactions, [])
        # Original (False AND True) deve ser Falso
        assert result.is_fraudulent == False

    def test_risk_score_accumulation(self):
        # Mata os mutantes 169 (+= 30 para = 30) e 188 (+= 20 para = 20)
        now = datetime.now()
        
        # Ativa Regra 1 (Valor Alto) e Regra 3 (Localização)
        current_transaction = Transaction(15000, now, "EUA")
        previous_transactions = [Transaction(100, now - timedelta(minutes=20), "Brasil")]
        
        result = self.system.check_for_fraud(current_transaction, previous_transactions, [])
        
        # Original: risk_score = 0 + 50 (Regra 1) + 20 (Regra 3) = 70
        # Mutante 188: risk_score = 50, depois risk_score = 20. (Falha)
        assert result.risk_score == 70
