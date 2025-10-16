import pytest
from datetime import datetime, timedelta
from src.flight.FlightBookingSystem import FlightBookingSystem
from src.flight.BookingResult import BookingResult

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