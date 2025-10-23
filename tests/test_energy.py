import pytest
from datetime import datetime
from src.energy.DeviceSchedule import DeviceSchedule
from src.energy.EnergyManagementSystem import SmartEnergyManagementSystem

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
        assert result.device_status["Heating"] == True  # Prioridade 1, não desliga
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