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
        
        # Determina os modos principais
        energy_saving_mode = current_price > price_threshold
        is_night_mode = current_time.hour >= 23 or current_time.hour < 6
        temperature_regulation_active = False
        
        # Salva o valor original, pois não devemos modificar o parâmetro de entrada
        initial_total_energy = total_energy_used_today

        # --- Lógica de Negócio Corrigida ---

        # 1. Definir Estado Base (Regra 2: Modo Noturno ou Modo Diurno Padrão)
        if is_night_mode:
            # Regra 2: Modo Noturno - Apenas essenciais ligados
            for device in device_status.keys():
                device_status[device] = device in ("Security", "Refrigerator")
        else:
            # Modo Diurno: Padrão é tudo ligado
            for device in device_status.keys():
                device_status[device] = True

        # 2. Aplicar Overrides de Desligamento (Economia e Limite)

        # Regra 1: Modo de Economia (Aplica-se apenas se NÃO for Modo Noturno)
        if not is_night_mode and energy_saving_mode:
            # Desliga dispositivos de baixa prioridade (prioridade > 1)
            for device, priority in device_priorities.items():
                if priority > 1:
                    device_status[device] = False

        # Regra 4: Limite de Consumo de Energia (Sempre verificado)
        # Desliga progressivamente P > 1.
        if total_energy_used_today >= energy_usage_limit:
            # Ordena da menor prioridade (maior número) para a maior (menor número)
            sorted_devices = sorted(device_priorities.items(), key=lambda item: item[1], reverse=True)
            
            for device, priority in sorted_devices:
                # Desliga apenas dispositivos de baixa prioridade (P > 1)
                if priority > 1 and device_status.get(device):
                    device_status[device] = False


        # 3. Aplicar Overrides de Ligação/Regulação (Temperatura e Agendados)

        # Regra 3: Regulação de Temperatura (Pode ligar dispositivos)
        temp_range = desired_temperature_range
        if current_temperature < temp_range[0]:
            if "Heating" in device_status:
                device_status["Heating"] = True # Força ligação
            if "Cooling" in device_status:
                device_status["Cooling"] = False # Força desligamento
            temperature_regulation_active = True
        elif current_temperature > temp_range[1]:
            if "Cooling" in device_status:
                device_status["Cooling"] = True # Força ligação
            if "Heating" in device_status:
                device_status["Heating"] = False # Força desligamento
            temperature_regulation_active = True
        
        # Regra 5: Dispositivos Agendados (Sobrepõe tudo)
        # Esta regra deve ser a última, pois ignora todos os outros modos.
        for schedule in scheduled_devices:
            if schedule.scheduled_time.hour == current_time.hour and schedule.scheduled_time.minute == current_time.minute:
                if schedule.device_name in device_status:
                    device_status[schedule.device_name] = True

        # Retorna o total de energia original, não um valor simulado
        return EnergyManagementResult(device_status, energy_saving_mode, temperature_regulation_active, initial_total_energy)