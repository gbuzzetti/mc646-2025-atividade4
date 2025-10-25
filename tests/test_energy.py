import pytest
from datetime import datetime
from energy.DeviceSchedule import DeviceSchedule
from energy.EnergyManagementSystem import SmartEnergyManagementSystem

class TestSmartEnergyManagementSystem:
    def setup_method(self):
        self.system = SmartEnergyManagementSystem()

    def test_no_energy_saving_mode(self):
        result = self.system.manage_energy(
            current_price=0.15,  # abaixo do limiar
            price_threshold=0.20,
            device_priorities={"Heating": 1, "Lights": 2},
            current_time=datetime(2024, 10, 1, 12, 0, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0,
            total_energy_used_today=10.0,
            scheduled_devices=[]
        )
        assert result.energy_saving_mode == False

    def test_scheduled_device_not_yet(self):
        schedule = DeviceSchedule("Oven", datetime(2024, 10, 1, 18, 0, 0))
        result = self.system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Oven": 2},
            current_time=datetime(2024, 10, 1, 17, 0, 0),  # antes do agendamento
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0,
            total_energy_used_today=25.0,
            scheduled_devices=[schedule]
        )
        assert result.device_status["Oven"] == False

    def test_energy_saving_mode(self):
        # Ativa o modo de economia quando o preço excede o limiar
        result = self.system.manage_energy(
            current_price=0.25,
            price_threshold=0.20,
            device_priorities={"Heating": 1, "Lights": 2, "Appliances": 3},
            current_time=datetime(2024, 10, 1, 12, 0, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0,
            total_energy_used_today=25.0,
            scheduled_devices=[]
        )
        assert result.energy_saving_mode == True
        # Dispositivos de prioridade 1 devem estar ligados, os outros desligados
        assert result.device_status["Heating"] == True
        assert result.device_status["Lights"] == False
        assert result.device_status["Appliances"] == False

    def test_night_mode(self):
        # Modo noturno desliga dispositivos não essenciais
        result = self.system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Security": 1, "Refrigerator": 1, "Lights": 2},
            current_time=datetime(2024, 10, 1, 23, 30, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0,
            total_energy_used_today=25.0,
            scheduled_devices=[]
        )
        # No modo noturno, apenas Security e Refrigerator permanecem ligados
        assert result.device_status["Security"] == True
        assert result.device_status["Refrigerator"] == True
        assert result.device_status["Lights"] == False

    def test_temperature_regulation_heating(self):
        # Liga o aquecimento se a temperatura estiver abaixo da faixa
        result = self.system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Heating": 1, "Cooling": 1},
            current_time=datetime(2024, 10, 1, 12, 0, 0),
            current_temperature=18.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0,
            total_energy_used_today=25.0,
            scheduled_devices=[]
        )
        assert result.temperature_regulation_active == True
        assert result.device_status["Heating"] == True
        assert result.device_status["Cooling"] == False

    def test_temperature_regulation_cooling(self):
        # Liga o resfriamento se a temperatura estiver acima da faixa
        result = self.system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Heating": 1, "Cooling": 1},
            current_time=datetime(2024, 10, 1, 12, 0, 0),
            current_temperature=25.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0,
            total_energy_used_today=25.0,
            scheduled_devices=[]
        )
        assert result.temperature_regulation_active == True
        assert result.device_status["Heating"] == False
        assert result.device_status["Cooling"] == True

    def test_energy_limit(self):
        # Desliga dispositivos de baixa prioridade quando o consumo está alto
        result = self.system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Heating": 1, "Lights": 2, "Appliances": 3},
            current_time=datetime(2024, 10, 1, 12, 0, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0,
            total_energy_used_today=35.0,  # Excede o limite
            scheduled_devices=[]
        )
        assert result.device_status["Lights"] == False
        assert result.device_status["Appliances"] == False
        assert result.device_status["Heating"] == False 
        assert result.total_energy_used == 33.0  # 35 - 2

    def test_scheduled_devices(self):
        # Dispositivos agendados devem ser ligados no horário agendado
        schedule = DeviceSchedule("Oven", datetime(2024, 10, 1, 12, 0, 0))
        result = self.system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Oven": 2},
            current_time=datetime(2024, 10, 1, 12, 0, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0,
            total_energy_used_today=25.0,
            scheduled_devices=[schedule]
        )
        # O dispositivo agendado deve estar ligado, mesmo sendo de baixa prioridade
        assert result.device_status["Oven"] == True

    # Novos testes após primeira análise dos resultados do mutmut

    def test_no_energy_saving_mode(self):
        # Original (Modificado para matar mutantes 13, 14)
        result = self.system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Heating": 1, "Lights": 2},
            current_time=datetime(2024, 10, 1, 12, 0, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0,
            total_energy_used_today=10.0,
            scheduled_devices=[]
        )
        assert result.energy_saving_mode == False
        # ADIÇÃO (Mata 13, 14):
        assert result.temperature_regulation_active == False

    def test_energy_saving_at_threshold(self):
        # Mata o mutante 3 (>= price_threshold)
        result = self.system.manage_energy(
            current_price=0.20, # Exatamente no limiar
            price_threshold=0.20,
            device_priorities={"Heating": 1},
            current_time=datetime(2024, 10, 1, 12, 0, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0,
            total_energy_used_today=10.0,
            scheduled_devices=[]
        )
        # Original (>) deve ser Falso
        assert result.energy_saving_mode == False

    def test_night_mode_at_boundary(self):
        # Mata os mutantes 7 (<= 6) e 8 (< 7)
        result = self.system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Lights": 2},
            current_time=datetime(2024, 10, 1, 6, 0, 0), # Exatamente 6:00
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0,
            total_energy_used_today=10.0,
            scheduled_devices=[]
        )
        # Original (< 6) deve ser Falso (não é mais noite)
        # No modo Diurno Normal, "Lights" deve ligar
        assert result.device_status["Lights"] == True

    def test_energy_limit_at_boundary(self):
        # Mata o mutante 11 (> energy_usage_limit)
        result = self.system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Lights": 2},
            current_time=datetime(2024, 10, 1, 12, 0, 0),
            current_temperature=22.0,
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0,
            total_energy_used_today=30.0,  # Exatamente no limite
            scheduled_devices=[]
        )
        # Original (>=) deve desligar "Lights"
        assert result.device_status["Lights"] == False

    def test_temperature_regulation_at_boundary(self):
        # Mata os mutantes 47 (<= temp_range[0]) e 61 (>= temp_range[1])
        
        # Teste 1: Limite inferior
        result = self.system.manage_energy(
            current_price=0.15, price_threshold=0.20,
            device_priorities={"Heating": 1},
            current_time=datetime(2024, 10, 1, 12, 0, 0),
            current_temperature=20.0, # Exatamente no limite
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0, total_energy_used_today=10.0, scheduled_devices=[]
        )
        # Original (<) não deve ligar o aquecedor
        assert result.device_status["Heating"] == False
        
        # Teste 2: Limite superior
        result = self.system.manage_energy(
            current_price=0.15, price_threshold=0.20,
            device_priorities={"Cooling": 1},
            current_time=datetime(2024, 10, 1, 12, 0, 0),
            current_temperature=24.0, # Exatamente no limite
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0, total_energy_used_today=10.0, scheduled_devices=[]
        )
        # Original (>) não deve ligar o ar
        assert result.device_status["Cooling"] == False

    def test_temperature_logic_with_missing_device(self):
        # Mata mutantes 50, 51, 64, 65 (e talvez 48, 49, 63)
        # Testa o que acontece se a temperatura está baixa, mas não há aquecedor
        result = self.system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Lights": 2, "Cooling": 1}, # Sem "Heating"
            current_time=datetime(2024, 10, 1, 12, 0, 0),
            current_temperature=18.0, # Precisa aquecer
            desired_temperature_range=(20.0, 24.0),
            energy_usage_limit=30.0,
            total_energy_used_today=25.0,
            scheduled_devices=[]
        )
        # Mutante 50 (not in) causaria um crash (KeyError)
        # Mutante 51 (KeyError) causaria um crash
        # O código original deve apenas rodar sem falhas
        assert result.temperature_regulation_active == True
        assert result.device_status["Cooling"] == False