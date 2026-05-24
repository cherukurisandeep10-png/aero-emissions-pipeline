"""
Emissions Calculator Module
Provides domain-specific modeling for aircraft fuel burn and CO2 emissions
based on real-time flight state vectors (velocity, altitude, climb/descent rates).
"""

import logging

logger = logging.getLogger(__name__)

# CO2 emission factor: 3.16 kg of CO2 produced per 1 kg of jet fuel burned (ICAO standard)
CO2_FACTOR = 3.16

class EmissionsCalculator:
    @staticmethod
    def infer_aircraft_type(velocity_mps: float, altitude_m: float) -> dict:
        """
        Infers the broad category of aircraft based on speed and altitude.
        Returns a dictionary with classification details and estimated base fuel burn rate (kg/second).
        """
        if velocity_mps is None or altitude_m is None:
            return {
                "category": "Unknown",
                "base_fuel_burn_kg_s": 0.8  # Default conservative average
            }
        
        # Convert mps to knots and meters to feet for aviation standard reasoning
        velocity_knots = velocity_mps * 1.94384
        altitude_ft = altitude_m * 3.28084
        
        if altitude_ft > 25000 and velocity_knots > 350:
            # High altitude, high speed -> likely a commercial widebody or narrowbody jet
            if velocity_knots > 450:
                return {
                    "category": "Widebody Jet (e.g., B777, B787, A350)",
                    "base_fuel_burn_kg_s": 1.6  # ~5,760 kg/hr
                }
            else:
                return {
                    "category": "Narrowbody Jet (e.g., B737, A320)",
                    "base_fuel_burn_kg_s": 0.75  # ~2,700 kg/hr
                }
        elif altitude_ft > 10000 and velocity_knots > 200:
            # Medium altitude/speed -> regional jet or turboprop
            if velocity_knots > 300:
                return {
                    "category": "Regional Jet (e.g., CRJ900, E190)",
                    "base_fuel_burn_kg_s": 0.45  # ~1,620 kg/hr
                }
            else:
                return {
                    "category": "Turboprop / Business Aviaton (e.g., ATR72, King Air)",
                    "base_fuel_burn_kg_s": 0.25  # ~900 kg/hr
                }
        else:
            # Low altitude, low speed -> light aircraft / general aviation or takeoff/landing phase
            return {
                "category": "Light Aircraft / General Aviation",
                "base_fuel_burn_kg_s": 0.08  # ~288 kg/hr
            }

    @classmethod
    def calculate_instantaneous_emissions(cls, velocity_mps: float, altitude_m: float, vertical_rate_mps: float = 0.0) -> dict:
        """
        Calculates instantaneous fuel burn and CO2 emissions.
        Factors in the flight phase: climbing burns more fuel, descending/cruising is standard.
        """
        classification = cls.infer_aircraft_type(velocity_mps, altitude_m)
        base_burn = classification["base_fuel_burn_kg_s"]
        
        # Adjust burn rate based on vertical rate (climbing vs descending)
        # Climbing requires significantly more thrust -> up to 40% increase
        # Descending requires minimal thrust (idle descent) -> up to 60% reduction
        multiplier = 1.0
        if vertical_rate_mps is not None:
            if vertical_rate_mps > 1.5:  # climbing at >300 ft/min
                multiplier = 1.35
            elif vertical_rate_mps < -1.5:  # descending at >300 ft/min
                multiplier = 0.40
                
        adjusted_burn = base_burn * multiplier
        co2_emissions_kg_s = adjusted_burn * CO2_FACTOR
        
        return {
            "aircraft_category": classification["category"],
            "base_fuel_burn_kg_s": base_burn,
            "adjusted_fuel_burn_kg_s": adjusted_burn,
            "co2_emissions_kg_s": co2_emissions_kg_s,
            "hourly_co2_metric_tonnes": (co2_emissions_kg_s * 3600) / 1000.0
        }
