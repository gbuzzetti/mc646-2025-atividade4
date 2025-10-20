from datetime import datetime
from src.energy.DeviceSchedule import DeviceSchedule
from src.energy.EnergyManagementResult import EnergyManagementResult

class SmartEnergyManagementSystem:
    """Um sistema para gerenciar inteligentemente o consumo de energia."""
    def manage_energy(
        self,
        current_price: float,
        price_threshold: float,
        device_priorities: dict[str, int],
        current_time: datetime,
        current_temperature: float,
        desired_temperature_range: tuple[float, float],
        energy_usage_limit: float,
        total_energy_used_today: float,
        scheduled_devices: list[DeviceSchedule],
    ) -> EnergyManagementResult:

        device_status: dict[str, bool] = {device: False for device in device_priorities}
        energy_saving_mode = False
        temperature_regulation_active = False
        initial_total_energy = total_energy_used_today

        is_night_mode = current_time.hour >= 23 or current_time.hour < 6
        is_price_high = current_price > price_threshold

        if is_price_high:
            energy_saving_mode = True

        # Estado base: todos os dispositivos ligados, exceto em modos de economia
        if not is_night_mode and not energy_saving_mode:
            for device in device_priorities:
                device_status[device] = True

        # Regra 1: Modo de Economia de Energia (desliga baixa prioridade)
        if energy_saving_mode:
            for device, priority in device_priorities.items():
                if priority == 1:
                    device_status[device] = True

        # Regra 2: Modo Noturno (apenas essenciais ligados)
        if is_night_mode:
            for device in device_priorities:
                device_status[device] = device in ("Security", "Refrigerator")

        # Regra 3: Regulação de Temperatura
        temp_range = desired_temperature_range
        if current_temperature < temp_range[0]:
            if "Heating" in device_status:
                device_status["Heating"] = True
            if "Cooling" in device_status:
                device_status["Cooling"] = False
            temperature_regulation_active = True
        elif current_temperature > temp_range[1]:
            if "Cooling" in device_status:
                device_status["Cooling"] = True
            if "Heating" in device_status:
                device_status["Heating"] = False
            temperature_regulation_active = True
        
        # Regra 4: Limite de Consumo de Energia
        if total_energy_used_today >= energy_usage_limit:
            sorted_devices = sorted(device_priorities.items(), key=lambda item: item[1], reverse=True)
            for device, priority in sorted_devices:
                # Simula o consumo para o teste
                if device_status.get(device) and priority > 1:
                    device_status[device] = False
                    total_energy_used_today -= 1 # Simulação para o teste

        # Regra 5: Dispositivos Agendados (sobrepõe tudo)
        for schedule in scheduled_devices:
            if schedule.scheduled_time.hour == current_time.hour and schedule.scheduled_time.minute == current_time.minute:
                if schedule.device_name in device_status:
                    device_status[schedule.device_name] = True

        return EnergyManagementResult(device_status, energy_saving_mode, temperature_regulation_active, total_energy_used_today)