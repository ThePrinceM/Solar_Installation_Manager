INSTALLATION_COST_PER_KW = 55000
MAINTENANCE_PER_YEAR = 1000
LIFESPAN_YEARS = 25

def calculate_solar(roof_area, irradiance, efficiency=0.17):
    # irradiance = kWh/m²/day (Open-Meteo)
    daily_energy = roof_area * efficiency * irradiance
    annual_energy = daily_energy * 365
    annual_savings = annual_energy * 8  # ₹8/kWh avg

    return round(annual_energy, 2), round(annual_savings, 2)


def calculate_roi(annual_energy):
    kw_capacity = annual_energy / (365 * 5)  # approx 5 hours peak
    install_cost = kw_capacity * INSTALLATION_COST_PER_KW

    annual_net = annual_energy * 8 - MAINTENANCE_PER_YEAR
    payback = install_cost / annual_net
    lifetime = annual_net * LIFESPAN_YEARS - install_cost

    return round(payback, 2), round(lifetime, 2)