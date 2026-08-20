"""
Physics & Flow-Density Traffic Scenario Simulator Engine
Problem Statement: AI/ML-09 / AML-05 (Innohack Project)

Simulates real-world traffic shockwave propagation, volume spikes, weather/rain impacts,
accident bottlenecks, and lane closures across urban arterial road networks.
"""

import math
import random
from typing import Dict, Any, List

class ScenarioSimulator:
    def __init__(self):
        # Base Indian urban corridor configuration benchmarks (Bengaluru Network)
        self.base_corridors = [
            {"id": "c1", "name": "Silk Board Junction", "base_speed": 12.0, "capacity_pcu": 35.0, "base_volume": 42.0, "cam": "CAM-3049"},
            {"id": "c2", "name": "Outer Ring Road (Bellandur)", "base_speed": 18.0, "capacity_pcu": 40.0, "base_volume": 36.0, "cam": "CAM-1923"},
            {"id": "c3", "name": "MG Road Signal", "base_speed": 24.0, "capacity_pcu": 30.0, "base_volume": 20.0, "cam": "CAM-0812"},
            {"id": "c4", "name": "Tin Factory (KR Puram)", "base_speed": 10.0, "capacity_pcu": 35.0, "base_volume": 44.0, "cam": "CAM-4120"},
            {"id": "c5", "name": "Hebbal Flyover Junction", "base_speed": 38.0, "capacity_pcu": 50.0, "base_volume": 22.0, "cam": "CAM-1055"},
            {"id": "c6", "name": "Koramangala 80ft Road", "base_speed": 28.0, "capacity_pcu": 30.0, "base_volume": 14.0, "cam": "CAM-0544"},
            {"id": "c7", "name": "Electronic City Expressway", "base_speed": 55.0, "capacity_pcu": 60.0, "base_volume": 25.0, "cam": "CAM-7711"},
            {"id": "c8", "name": "Indiranagar 100ft Road", "base_speed": 22.0, "capacity_pcu": 32.0, "base_volume": 21.0, "cam": "CAM-2219"}
        ]

    def simulate_scenario(self, 
                          volume_multiplier: float = 1.0, 
                          rain_active: bool = False, 
                          accident_corridor: str = None, 
                          lane_closure_active: bool = False) -> Dict[str, Any]:
        """
        Calculates network shockwaves, PCU densities, speed reduction, and delays under custom simulated conditions.
        """
        simulated_results = []
        total_pcu_load = 0.0
        active_incidents = []

        # Environmental factors impact
        rain_factor = 1.25 if rain_active else 1.0
        closure_factor = 1.40 if lane_closure_active else 1.0

        for c in self.base_corridors:
            # Check if this corridor has an active accident
            is_accident = (accident_corridor and (accident_corridor.lower() in c["name"].lower() or c["id"] == accident_corridor))
            accident_factor = 2.10 if is_accident else 1.0

            # Calculate simulated volume and PCU load
            sim_volume = c["base_volume"] * volume_multiplier * rain_factor * closure_factor * accident_factor
            sim_pcu = round(sim_volume * 0.85, 1) # Avg PCU weight multiplier
            total_pcu_load += sim_pcu

            # Calculate congestion percentage against corridor capacity
            congestion_pct = min(99.0, round((sim_pcu / c["capacity_pcu"]) * 100.0, 1))

            # Calculate dynamic speed reduction via Greenshields Traffic Stream Model
            free_flow_speed = c["base_speed"] * 1.5
            speed_reduction = (congestion_pct / 100.0) ** 1.3
            sim_speed = round(max(5.0, free_flow_speed * (1.0 - (0.85 * speed_reduction))), 1)

            # Delay calculation (additional delay in minutes)
            base_travel_time = (10.0 / c["base_speed"]) * 60.0 # 10km corridor
            sim_travel_time = (10.0 / sim_speed) * 60.0
            delay_min = round(max(0.5, sim_travel_time - base_travel_time), 1)

            # Status determination
            if is_accident:
                status = "CRITICAL ACCIDENT"
                color = "#FB6169"
                active_incidents.append({
                    "corridor": c["name"],
                    "type": "Vehicle Collision & Bottleneck",
                    "severity": "CRITICAL",
                    "speed_drop": f"{c['base_speed']} km/h → {sim_speed} km/h",
                    "action_required": "Reroute Traffic & Dispatch Emergency Unit"
                })
            elif congestion_pct > 80.0:
                status = "SEVERE"
                color = "#FB6169"
            elif congestion_pct > 55.0:
                status = "MODERATE"
                color = "#FFB547"
            else:
                status = "CLEAR"
                color = "#34D399"

            simulated_results.append({
                "id": c["id"],
                "name": c["name"],
                "cam": c["cam"],
                "congestion_pct": congestion_pct,
                "simulated_speed_kmh": sim_speed,
                "delay_min": delay_min,
                "pcu_load": sim_pcu,
                "status": status,
                "color": color,
                "is_accident": is_accident
            })

        avg_congestion = round(sum(r["congestion_pct"] for r in simulated_results) / len(simulated_results), 1)
        
        # Calculate Sustainability Multi-Objective Metrics
        time_saved_min = round(sum(r["delay_min"] for r in simulated_results) * 0.45, 1)
        fuel_saved_liters = round(time_saved_min * 0.18, 1)
        co2_saved_kg = round(fuel_saved_liters * 2.31, 1) # 2.31kg CO2 per liter petrol

        # Explainable AI (XAI) Congestion Breakdown
        base_contrib = 40.0
        volume_contrib = round(min(45.0, (volume_multiplier - 1.0) * 50.0 + 15.0), 1) if volume_multiplier > 1.0 else 15.0
        weather_contrib = 22.0 if rain_active else 5.0
        incident_contrib = 30.0 if accident_corridor else 8.0
        closure_contrib = 20.0 if lane_closure_active else 5.0

        total_factors = volume_contrib + weather_contrib + incident_contrib + closure_contrib + base_contrib
        xai_breakdown = [
            {"factor": "Traffic Volume Spike", "pct": round((volume_contrib / total_factors) * 100, 1), "color": "#4DD6FF"},
            {"factor": "Weather / Rain Impact", "pct": round((weather_contrib / total_factors) * 100, 1), "color": "#FFB547"},
            {"factor": "Incidents & Bottlenecks", "pct": round((incident_contrib / total_factors) * 100, 1), "color": "#FB6169"},
            {"factor": "Lane Closure / Roadworks", "pct": round((closure_contrib / total_factors) * 100, 1), "color": "#34D399"}
        ]

        return {
            "simulation_active": True,
            "params": {
                "volume_multiplier": volume_multiplier,
                "rain_active": rain_active,
                "accident_corridor": accident_corridor,
                "lane_closure_active": lane_closure_active
            },
            "summary": {
                "avg_congestion_pct": avg_congestion,
                "total_pcu_load": round(total_pcu_load, 1),
                "active_incidents_count": len(active_incidents),
                "time_saved_min": time_saved_min,
                "fuel_saved_liters": fuel_saved_liters,
                "co2_saved_kg": co2_saved_kg
            },
            "incidents": active_incidents,
            "xai_breakdown": xai_breakdown,
            "corridors": simulated_results
        }
