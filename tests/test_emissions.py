import pytest
from src.emissions_calculator import EmissionsCalculator

def test_aircraft_classification_widebody():
    classification = EmissionsCalculator.infer_aircraft_type(velocity_mps=250.0, altitude_m=10000.0)
    assert "Widebody" in classification["category"]
    assert classification["base_fuel_burn_kg_s"] == 1.6

def test_aircraft_classification_light():
    classification = EmissionsCalculator.infer_aircraft_type(velocity_mps=50.0, altitude_m=1000.0)
    assert "Light" in classification["category"]
    assert classification["base_fuel_burn_kg_s"] == 0.08

def test_emissions_factor_climbing():
    emissions = EmissionsCalculator.calculate_instantaneous_emissions(
        velocity_mps=200.0, altitude_m=8000.0, vertical_rate_mps=5.0
    )
    assert emissions["adjusted_fuel_burn_kg_s"] > emissions["base_fuel_burn_kg_s"]
