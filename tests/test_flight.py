import pytest
from datetime import datetime, timedelta
from flight.FlightBookingSystem import FlightBookingSystem
from flight.BookingResult import BookingResult

class TestFlightBookingSystem:
    def setup_method(self):
        self.system = FlightBookingSystem()

    def test_reward_points_exceeding_price(self):
        booking_time = datetime.now()
        departure_time = booking_time + timedelta(days=2)
        result = self.system.book_flight(
            passengers=1,
            booking_time=booking_time,
            available_seats=100,
            current_price=100.0,
            previous_sales=10,
            is_cancellation=False,
            departure_time=departure_time,
            reward_points_available=20000  # 20000 * 0.01 = 200 > preço
        )
        assert result.confirmation == True
        assert result.total_price == 0.0  # deve truncar preço negativo

    def test_insufficient_seats(self):
        # Teste para quando não há assentos suficientes
        booking_time = datetime.now()
        departure_time = booking_time + timedelta(days=1)
        result = self.system.book_flight(
            passengers=5,
            booking_time=booking_time,
            available_seats=4,
            current_price=500.0,
            previous_sales=50,
            is_cancellation=False,
            departure_time=departure_time,
            reward_points_available=0
        )
        assert result.confirmation == False

    def test_successful_booking(self):
        # Reserva bem-sucedida sem cancelamento, sem taxa de última hora, sem desconto de grupo, sem pontos
        booking_time = datetime.now()
        departure_time = booking_time + timedelta(days=2)  # Mais de 24 horas
        result = self.system.book_flight(
            passengers=2,
            booking_time=booking_time,
            available_seats=100,
            current_price=500.0,
            previous_sales=50,
            is_cancellation=False,
            departure_time=departure_time,
            reward_points_available=0
        )
        assert result.confirmation == True
        # Preço dinâmico: (50/100)*0.8 = 0.4 -> 500 * 0.4 * 2 = 400
        assert result.total_price == 400.0
        assert result.points_used == False

    def test_last_minute_booking(self):
        # Reserva com taxa de última hora
        booking_time = datetime.now()
        departure_time = booking_time + timedelta(hours=23)  # Menos de 24 horas
        result = self.system.book_flight(
            passengers=2,
            booking_time=booking_time,
            available_seats=100,
            current_price=500.0,
            previous_sales=50,
            is_cancellation=False,
            departure_time=departure_time,
            reward_points_available=0
        )
        assert result.confirmation == True
        # Preço dinâmico: 400 + 100 = 500
        assert result.total_price == 500.0

    def test_group_discount(self):
        # Reserva com desconto de grupo
        booking_time = datetime.now()
        departure_time = booking_time + timedelta(days=2)
        result = self.system.book_flight(
            passengers=5,
            booking_time=booking_time,
            available_seats=100,
            current_price=500.0,
            previous_sales=50,
            is_cancellation=False,
            departure_time=departure_time,
            reward_points_available=0
        )
        assert result.confirmation == True
        # Preço dinâmico: 500 * 0.4 * 5 = 1000, depois desconto de 5% -> 950
        assert result.total_price == 950.0

    def test_reward_points(self):
        # Reserva com uso de pontos
        booking_time = datetime.now()
        departure_time = booking_time + timedelta(days=2)
        result = self.system.book_flight(
            passengers=2,
            booking_time=booking_time,
            available_seats=100,
            current_price=500.0,
            previous_sales=50,
            is_cancellation=False,
            departure_time=departure_time,
            reward_points_available=10000  # 10000 * 0.01 = 100
        )
        assert result.confirmation == True
        # Preço dinâmico: 400, depois pontos: 400 - 100 = 300
        assert result.total_price == 300.0
        assert result.points_used == True

    def test_cancellation_more_than_48h(self):
        # Cancelamento com mais de 48 horas -> reembolso total
        booking_time = datetime.now()
        departure_time = booking_time + timedelta(hours=49)
        result = self.system.book_flight(
            passengers=2,
            booking_time=booking_time,
            available_seats=100,
            current_price=500.0,
            previous_sales=50,
            is_cancellation=True,
            departure_time=departure_time,
            reward_points_available=0
        )
        assert result.confirmation == False
        # O preço total seria 400, então reembolso total
        assert result.refund_amount == 400.0

    def test_cancellation_less_than_48h(self):
        # Cancelamento com menos de 48 horas -> reembolso 50%
        booking_time = datetime.now()
        departure_time = booking_time + timedelta(hours=47)
        result = self.system.book_flight(
            passengers=2,
            booking_time=booking_time,
            available_seats=100,
            current_price=500.0,
            previous_sales=50,
            is_cancellation=True,
            departure_time=departure_time,
            reward_points_available=0
        )
        assert result.confirmation == False
        assert result.refund_amount == 400.0 * 0.5

    # Novos testes após a primeira análise dos resultados do mutmut

    def test_insufficient_seats(self):
        # Original (Modificado para matar mutantes 81-84)
        booking_time = datetime.now()
        departure_time = booking_time + timedelta(days=1)
        result = self.system.book_flight(
            passengers=5,
            booking_time=booking_time,
            available_seats=4,
            current_price=500.0,
            previous_sales=50,
            is_cancellation=False,
            departure_time=departure_time,
            reward_points_available=0
        )
        assert result.confirmation == False
        # ADIÇÕES (Matam 81, 82, 83, 84):
        assert result.total_price == 0.0, "Preço deve ser 0 em falha"
        assert result.refund_amount == 0.0, "Reembolso deve ser 0 em falha"

    def test_cancellation_more_than_48h(self):
        # Original (Modificado para matar mutantes 132, 133)
        booking_time = datetime.now()
        departure_time = booking_time + timedelta(hours=49)
        result = self.system.book_flight(
            passengers=2,
            booking_time=booking_time,
            available_seats=100,
            current_price=500.0,
            previous_sales=50,
            is_cancellation=True,
            departure_time=departure_time,
            reward_points_available=0
        )
        assert result.confirmation == False
        assert result.refund_amount == 400.0
        # ADIÇÕES (Matam 132, 133):
        assert result.total_price == 0.0, "Preço deve ser 0 em cancelamento"
        assert result.points_used == False, "Pontos não devem ser usados em cancelamento"

    def test_last_minute_booking_at_boundary(self):
        # Mata os mutantes 103 (<= 24) e 104 (< 25)
        booking_time = datetime.now()
        # Exatamente 24 horas
        departure_time = booking_time + timedelta(hours=24)
        result = self.system.book_flight(
            passengers=1, booking_time=booking_time, available_seats=100,
            current_price=500.0, previous_sales=50, is_cancellation=False,
            departure_time=departure_time, reward_points_available=0
        )
        # Original (< 24) não deve aplicar taxa
        assert result.total_price == (500.0 * (50/100.0) * 0.8 * 1) # 200.0
        assert result.total_price == 200.0

    def test_group_discount_at_boundary(self):
        # Mata o mutante 108 (>= 4)
        booking_time = datetime.now()
        departure_time = booking_time + timedelta(days=2)
        # Exatamente 4 passageiros
        result = self.system.book_flight(
            passengers=4, booking_time=booking_time, available_seats=100,
            current_price=500.0, previous_sales=50, is_cancellation=False,
            departure_time=departure_time, reward_points_available=0
        )
        # Original (> 4) não deve aplicar desconto
        # Preço: 500 * 0.4 * 4 = 800
        assert result.total_price == 800.0

    def test_reward_points_at_boundary(self):
        # Mata o mutante 114 (> 1)
        booking_time = datetime.now()
        departure_time = booking_time + timedelta(days=2)
        # Exatamente 1 ponto (deve ser usado)
        result = self.system.book_flight(
            passengers=1, booking_time=booking_time, available_seats=100,
            current_price=500.0, previous_sales=50, is_cancellation=False,
            departure_time=departure_time, reward_points_available=1
        )
        # Original (> 0) deve usar o ponto
        assert result.points_used == True
        # Preço: 200 - (1 * 0.01) = 199.99
        assert result.total_price == 199.99

    def test_cancellation_at_48h_boundary(self):
        # Mata o mutante 125 (> 48)
        booking_time = datetime.now()
        departure_time = booking_time + timedelta(hours=48) # Exatamente 48h
        result = self.system.book_flight(
            passengers=2, booking_time=booking_time, available_seats=100,
            current_price=500.0, previous_sales=50, is_cancellation=True,
            departure_time=departure_time, reward_points_available=0
        )
        # Original (>= 48) deve dar reembolso total (400)
        assert result.refund_amount == 400.0