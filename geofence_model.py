"""
Geofence Radius Prediction Model
================================

A simple, production-ready lookup module for predicting optimal geofence
radii based on property type, address source, and population density.

Based on analysis of 26.8M delivery records from Chirag_dx.20250501_dlvrd_distance

Usage:
    from geofence_model import get_geofence_radius, get_density_category
    
    # Get radius for a specific combination
    radius = get_geofence_radius(
        property_type="HOUSE",
        address_source="AMS", 
        density_category="SUBURBAN"
    )
    
    # Or derive density from population
    density = get_density_category(population_per_km2=500)
    radius = get_geofence_radius("APARTMENT", "GOOGLE", density)

Author: Code Puppy 🐶
Date: January 29, 2026
"""

from typing import Literal, Optional
from enum import Enum


# =============================================================================
# Type Definitions
# =============================================================================

class PropertyType(str, Enum):
    HOUSE = "HOUSE"
    APARTMENT = "APARTMENT"
    BUSINESS = "BUSINESS"
    MOBILE_HOME = "MOBILE_HOME"
    DORM = "DORM"
    OTHER = "OTHER"


class AddressSource(str, Enum):
    AMS = "AMS"
    GOOGLE = "GOOGLE"
    MAPBOX = "MAPBOX"
    CUSTOMER_PIN = "CUSTOMER_PIN"
    MANUAL_ADJ = "MANUAL_ADJ"


class DensityCategory(str, Enum):
    URBAN_HIGH = "URBAN_HIGH"      # > 4000 people/km²
    URBAN_MEDIUM = "URBAN_MEDIUM"  # 1000-4000 people/km²
    SUBURBAN = "SUBURBAN"          # 200-1000 people/km²
    RURAL = "RURAL"                # < 200 people/km²


class AccessRequired(str, Enum):
    YES = "YES"    # Gated community, buzzer, access code needed
    NO = "NO"      # No access restrictions


# =============================================================================
# Geofence Lookup Table (P95 Percentile - captures 95% of deliveries)
# =============================================================================

# Structure: (density, property_type, address_source) -> radius_meters
GEOFENCE_LOOKUP: dict[tuple[str, str, str], int] = {
    # URBAN_HIGH (>4000 people/km²)
    ("URBAN_HIGH", "HOUSE", "AMS"): 28,
    ("URBAN_HIGH", "HOUSE", "GOOGLE"): 70,
    ("URBAN_HIGH", "HOUSE", "MAPBOX"): 85,

    ("URBAN_HIGH", "HOUSE", "CUSTOMER_PIN"): 400,
    ("URBAN_HIGH", "APARTMENT", "AMS"): 45,
    ("URBAN_HIGH", "APARTMENT", "GOOGLE"): 140,
    ("URBAN_HIGH", "APARTMENT", "MAPBOX"): 150,

    ("URBAN_HIGH", "APARTMENT", "CUSTOMER_PIN"): 450,
    ("URBAN_HIGH", "BUSINESS", "AMS"): 48,
    ("URBAN_HIGH", "BUSINESS", "GOOGLE"): 100,
    ("URBAN_HIGH", "BUSINESS", "MAPBOX"): 120,

    ("URBAN_HIGH", "BUSINESS", "CUSTOMER_PIN"): 400,
    ("URBAN_HIGH", "MOBILE_HOME", "AMS"): 25,
    ("URBAN_HIGH", "MOBILE_HOME", "GOOGLE"): 70,
    ("URBAN_HIGH", "MOBILE_HOME", "MAPBOX"): 80,

    ("URBAN_HIGH", "MOBILE_HOME", "CUSTOMER_PIN"): 400,
    ("URBAN_HIGH", "DORM", "AMS"): 200,
    ("URBAN_HIGH", "DORM", "GOOGLE"): 220,
    ("URBAN_HIGH", "DORM", "MAPBOX"): 230,

    ("URBAN_HIGH", "DORM", "CUSTOMER_PIN"): 500,
    ("URBAN_HIGH", "OTHER", "AMS"): 70,
    ("URBAN_HIGH", "OTHER", "GOOGLE"): 120,
    ("URBAN_HIGH", "OTHER", "MAPBOX"): 130,

    ("URBAN_HIGH", "OTHER", "CUSTOMER_PIN"): 450,
    
    # URBAN_MEDIUM (1000-4000 people/km²)
    ("URBAN_MEDIUM", "HOUSE", "AMS"): 29,
    ("URBAN_MEDIUM", "HOUSE", "GOOGLE"): 72,
    ("URBAN_MEDIUM", "HOUSE", "MAPBOX"): 88,

    ("URBAN_MEDIUM", "HOUSE", "CUSTOMER_PIN"): 420,
    ("URBAN_MEDIUM", "APARTMENT", "AMS"): 45,
    ("URBAN_MEDIUM", "APARTMENT", "GOOGLE"): 145,
    ("URBAN_MEDIUM", "APARTMENT", "MAPBOX"): 155,

    ("URBAN_MEDIUM", "APARTMENT", "CUSTOMER_PIN"): 480,
    ("URBAN_MEDIUM", "BUSINESS", "AMS"): 50,
    ("URBAN_MEDIUM", "BUSINESS", "GOOGLE"): 100,
    ("URBAN_MEDIUM", "BUSINESS", "MAPBOX"): 120,

    ("URBAN_MEDIUM", "BUSINESS", "CUSTOMER_PIN"): 420,
    ("URBAN_MEDIUM", "MOBILE_HOME", "AMS"): 26,
    ("URBAN_MEDIUM", "MOBILE_HOME", "GOOGLE"): 72,
    ("URBAN_MEDIUM", "MOBILE_HOME", "MAPBOX"): 82,

    ("URBAN_MEDIUM", "MOBILE_HOME", "CUSTOMER_PIN"): 420,
    ("URBAN_MEDIUM", "DORM", "AMS"): 210,
    ("URBAN_MEDIUM", "DORM", "GOOGLE"): 225,
    ("URBAN_MEDIUM", "DORM", "MAPBOX"): 235,

    ("URBAN_MEDIUM", "DORM", "CUSTOMER_PIN"): 520,
    ("URBAN_MEDIUM", "OTHER", "AMS"): 72,
    ("URBAN_MEDIUM", "OTHER", "GOOGLE"): 125,
    ("URBAN_MEDIUM", "OTHER", "MAPBOX"): 135,

    ("URBAN_MEDIUM", "OTHER", "CUSTOMER_PIN"): 470,
    
    # SUBURBAN (200-1000 people/km²)
    ("SUBURBAN", "HOUSE", "AMS"): 30,
    ("SUBURBAN", "HOUSE", "GOOGLE"): 75,
    ("SUBURBAN", "HOUSE", "MAPBOX"): 90,

    ("SUBURBAN", "HOUSE", "CUSTOMER_PIN"): 450,
    ("SUBURBAN", "APARTMENT", "AMS"): 40,
    ("SUBURBAN", "APARTMENT", "GOOGLE"): 130,
    ("SUBURBAN", "APARTMENT", "MAPBOX"): 140,

    ("SUBURBAN", "APARTMENT", "CUSTOMER_PIN"): 500,
    ("SUBURBAN", "BUSINESS", "AMS"): 50,
    ("SUBURBAN", "BUSINESS", "GOOGLE"): 100,
    ("SUBURBAN", "BUSINESS", "MAPBOX"): 120,

    ("SUBURBAN", "BUSINESS", "CUSTOMER_PIN"): 450,
    ("SUBURBAN", "MOBILE_HOME", "AMS"): 28,
    ("SUBURBAN", "MOBILE_HOME", "GOOGLE"): 75,
    ("SUBURBAN", "MOBILE_HOME", "MAPBOX"): 85,

    ("SUBURBAN", "MOBILE_HOME", "CUSTOMER_PIN"): 450,
    ("SUBURBAN", "DORM", "AMS"): 216,
    ("SUBURBAN", "DORM", "GOOGLE"): 230,
    ("SUBURBAN", "DORM", "MAPBOX"): 240,

    ("SUBURBAN", "DORM", "CUSTOMER_PIN"): 550,
    ("SUBURBAN", "OTHER", "AMS"): 75,
    ("SUBURBAN", "OTHER", "GOOGLE"): 130,
    ("SUBURBAN", "OTHER", "MAPBOX"): 140,

    ("SUBURBAN", "OTHER", "CUSTOMER_PIN"): 500,
    
    # RURAL (<200 people/km²)
    ("RURAL", "HOUSE", "AMS"): 34,
    ("RURAL", "HOUSE", "GOOGLE"): 80,
    ("RURAL", "HOUSE", "MAPBOX"): 95,

    ("RURAL", "HOUSE", "CUSTOMER_PIN"): 500,
    ("RURAL", "APARTMENT", "AMS"): 50,
    ("RURAL", "APARTMENT", "GOOGLE"): 160,
    ("RURAL", "APARTMENT", "MAPBOX"): 170,

    ("RURAL", "APARTMENT", "CUSTOMER_PIN"): 550,
    ("RURAL", "BUSINESS", "AMS"): 55,
    ("RURAL", "BUSINESS", "GOOGLE"): 110,
    ("RURAL", "BUSINESS", "MAPBOX"): 130,

    ("RURAL", "BUSINESS", "CUSTOMER_PIN"): 500,
    ("RURAL", "MOBILE_HOME", "AMS"): 30,
    ("RURAL", "MOBILE_HOME", "GOOGLE"): 80,
    ("RURAL", "MOBILE_HOME", "MAPBOX"): 90,

    ("RURAL", "MOBILE_HOME", "CUSTOMER_PIN"): 500,
    ("RURAL", "DORM", "AMS"): 220,
    ("RURAL", "DORM", "GOOGLE"): 240,
    ("RURAL", "DORM", "MAPBOX"): 250,

    ("RURAL", "DORM", "CUSTOMER_PIN"): 600,
    ("RURAL", "OTHER", "AMS"): 80,
    ("RURAL", "OTHER", "GOOGLE"): 140,
    ("RURAL", "OTHER", "MAPBOX"): 150,

    ("RURAL", "OTHER", "CUSTOMER_PIN"): 550,
}

# Default fallback radii by property type (when source/density unknown)
DEFAULT_BY_PROPERTY: dict[str, int] = {
    "HOUSE": 50,
    "APARTMENT": 85,
    "BUSINESS": 75,
    "MOBILE_HOME": 45,
    "DORM": 220,
    "OTHER": 100,
}

# =============================================================================
# Arrival Radius Lookup Table (P95 Percentile - where driver parks)
# Based on ARRVL_DIST_METER analysis from Chirag_dx.20250501_dlvrd_distance
# Now with proper density breakdowns for consistency with delivery lookup!
# =============================================================================

# Structure: (density, property_type, address_source) -> radius_meters
ARRIVAL_GEOFENCE_LOOKUP: dict[tuple[str, str, str], int] = {
    # URBAN_HIGH (>4000 people/km²)
    ("URBAN_HIGH", "HOUSE", "AMS"): 36,
    ("URBAN_HIGH", "HOUSE", "GOOGLE"): 50,
    ("URBAN_HIGH", "HOUSE", "MAPBOX"): 55,
    ("URBAN_HIGH", "HOUSE", "CUSTOMER_PIN"): 138,
    ("URBAN_HIGH", "APARTMENT", "AMS"): 69,
    ("URBAN_HIGH", "APARTMENT", "GOOGLE"): 92,
    ("URBAN_HIGH", "APARTMENT", "MAPBOX"): 86,
    ("URBAN_HIGH", "APARTMENT", "CUSTOMER_PIN"): 107,
    ("URBAN_HIGH", "BUSINESS", "AMS"): 65,
    ("URBAN_HIGH", "BUSINESS", "GOOGLE"): 114,
    ("URBAN_HIGH", "BUSINESS", "MAPBOX"): 100,
    ("URBAN_HIGH", "BUSINESS", "CUSTOMER_PIN"): 200,
    ("URBAN_HIGH", "MOBILE_HOME", "AMS"): 36,
    ("URBAN_HIGH", "MOBILE_HOME", "GOOGLE"): 50,
    ("URBAN_HIGH", "MOBILE_HOME", "MAPBOX"): 55,
    ("URBAN_HIGH", "MOBILE_HOME", "CUSTOMER_PIN"): 138,
    ("URBAN_HIGH", "DORM", "AMS"): 91,
    ("URBAN_HIGH", "DORM", "GOOGLE"): 138,
    ("URBAN_HIGH", "DORM", "MAPBOX"): 150,
    ("URBAN_HIGH", "DORM", "CUSTOMER_PIN"): 200,
    ("URBAN_HIGH", "OTHER", "AMS"): 64,
    ("URBAN_HIGH", "OTHER", "GOOGLE"): 138,
    ("URBAN_HIGH", "OTHER", "MAPBOX"): 120,
    ("URBAN_HIGH", "OTHER", "CUSTOMER_PIN"): 200,
    
    # URBAN_MEDIUM (1000-4000 people/km²)
    ("URBAN_MEDIUM", "HOUSE", "AMS"): 35,
    ("URBAN_MEDIUM", "HOUSE", "GOOGLE"): 51,
    ("URBAN_MEDIUM", "HOUSE", "MAPBOX"): 52,
    ("URBAN_MEDIUM", "HOUSE", "CUSTOMER_PIN"): 144,
    ("URBAN_MEDIUM", "APARTMENT", "AMS"): 68,
    ("URBAN_MEDIUM", "APARTMENT", "GOOGLE"): 152,
    ("URBAN_MEDIUM", "APARTMENT", "MAPBOX"): 127,
    ("URBAN_MEDIUM", "APARTMENT", "CUSTOMER_PIN"): 183,
    ("URBAN_MEDIUM", "BUSINESS", "AMS"): 64,
    ("URBAN_MEDIUM", "BUSINESS", "GOOGLE"): 143,
    ("URBAN_MEDIUM", "BUSINESS", "MAPBOX"): 119,
    ("URBAN_MEDIUM", "BUSINESS", "CUSTOMER_PIN"): 188,
    ("URBAN_MEDIUM", "MOBILE_HOME", "AMS"): 35,
    ("URBAN_MEDIUM", "MOBILE_HOME", "GOOGLE"): 51,
    ("URBAN_MEDIUM", "MOBILE_HOME", "MAPBOX"): 52,
    ("URBAN_MEDIUM", "MOBILE_HOME", "CUSTOMER_PIN"): 144,
    ("URBAN_MEDIUM", "DORM", "AMS"): 91,
    ("URBAN_MEDIUM", "DORM", "GOOGLE"): 180,
    ("URBAN_MEDIUM", "DORM", "MAPBOX"): 185,
    ("URBAN_MEDIUM", "DORM", "CUSTOMER_PIN"): 244,
    ("URBAN_MEDIUM", "OTHER", "AMS"): 60,
    ("URBAN_MEDIUM", "OTHER", "GOOGLE"): 180,
    ("URBAN_MEDIUM", "OTHER", "MAPBOX"): 185,
    ("URBAN_MEDIUM", "OTHER", "CUSTOMER_PIN"): 244,
    
    # SUBURBAN (200-1000 people/km²)
    ("SUBURBAN", "HOUSE", "AMS"): 38,
    ("SUBURBAN", "HOUSE", "GOOGLE"): 59,
    ("SUBURBAN", "HOUSE", "MAPBOX"): 58,
    ("SUBURBAN", "HOUSE", "CUSTOMER_PIN"): 244,
    ("SUBURBAN", "APARTMENT", "AMS"): 60,
    ("SUBURBAN", "APARTMENT", "GOOGLE"): 176,
    ("SUBURBAN", "APARTMENT", "MAPBOX"): 150,
    ("SUBURBAN", "APARTMENT", "CUSTOMER_PIN"): 232,
    ("SUBURBAN", "BUSINESS", "AMS"): 65,
    ("SUBURBAN", "BUSINESS", "GOOGLE"): 168,
    ("SUBURBAN", "BUSINESS", "MAPBOX"): 176,
    ("SUBURBAN", "BUSINESS", "CUSTOMER_PIN"): 266,
    ("SUBURBAN", "MOBILE_HOME", "AMS"): 38,
    ("SUBURBAN", "MOBILE_HOME", "GOOGLE"): 59,
    ("SUBURBAN", "MOBILE_HOME", "MAPBOX"): 58,
    ("SUBURBAN", "MOBILE_HOME", "CUSTOMER_PIN"): 244,
    ("SUBURBAN", "DORM", "AMS"): 91,
    ("SUBURBAN", "DORM", "GOOGLE"): 253,
    ("SUBURBAN", "DORM", "MAPBOX"): 201,
    ("SUBURBAN", "DORM", "CUSTOMER_PIN"): 426,
    ("SUBURBAN", "OTHER", "AMS"): 62,
    ("SUBURBAN", "OTHER", "GOOGLE"): 253,
    ("SUBURBAN", "OTHER", "MAPBOX"): 201,
    ("SUBURBAN", "OTHER", "CUSTOMER_PIN"): 426,
    
    # RURAL (<200 people/km²)
    ("RURAL", "HOUSE", "AMS"): 42,
    ("RURAL", "HOUSE", "GOOGLE"): 110,
    ("RURAL", "HOUSE", "MAPBOX"): 119,
    ("RURAL", "HOUSE", "CUSTOMER_PIN"): 763,
    ("RURAL", "APARTMENT", "AMS"): 57,
    ("RURAL", "APARTMENT", "GOOGLE"): 164,
    ("RURAL", "APARTMENT", "MAPBOX"): 144,
    ("RURAL", "APARTMENT", "CUSTOMER_PIN"): 345,
    ("RURAL", "BUSINESS", "AMS"): 69,
    ("RURAL", "BUSINESS", "GOOGLE"): 196,
    ("RURAL", "BUSINESS", "MAPBOX"): 250,
    ("RURAL", "BUSINESS", "CUSTOMER_PIN"): 529,
    ("RURAL", "MOBILE_HOME", "AMS"): 42,
    ("RURAL", "MOBILE_HOME", "GOOGLE"): 110,
    ("RURAL", "MOBILE_HOME", "MAPBOX"): 119,
    ("RURAL", "MOBILE_HOME", "CUSTOMER_PIN"): 763,
    ("RURAL", "DORM", "AMS"): 91,
    ("RURAL", "DORM", "GOOGLE"): 294,
    ("RURAL", "DORM", "MAPBOX"): 302,
    ("RURAL", "DORM", "CUSTOMER_PIN"): 1014,
    ("RURAL", "OTHER", "AMS"): 73,
    ("RURAL", "OTHER", "GOOGLE"): 294,
    ("RURAL", "OTHER", "MAPBOX"): 302,
    ("RURAL", "OTHER", "CUSTOMER_PIN"): 1014,
}

# Default fallback arrival radii by property type
DEFAULT_ARRIVAL_BY_PROPERTY: dict[str, int] = {
    "HOUSE": 50,
    "APARTMENT": 80,
    "BUSINESS": 80,
    "MOBILE_HOME": 50,
    "DORM": 150,
    "OTHER": 80,
}

# Ultimate fallback
DEFAULT_RADIUS: int = 50

# Access code multipliers by property type
# Based on P95 analysis: access_true / access_false ratios
# Apartments are most affected (~28%), houses barely affected (~1%)
ACCESS_MULTIPLIERS: dict[str, float] = {
    "APARTMENT": 1.28,    # 39.99m vs 31.30m = 28% increase
    "BUSINESS": 1.16,     # 48.66m vs 41.96m = 16% increase
    "DORM": 1.10,         # Estimated - dorms often have access
    "HOUSE": 1.01,        # 29.93m vs 29.66m = 1% (negligible)
    "MOBILE_HOME": 1.0,   # No significant data
    "OTHER": 1.0,         # No significant difference
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_density_category(population_per_km2: float) -> str:
    """
    Convert population density (people/km²) to density category.
    
    Args:
        population_per_km2: Population density in people per square kilometer
        
    Returns:
        str: One of URBAN_HIGH, URBAN_MEDIUM, SUBURBAN, RURAL
    """
    if population_per_km2 > 4000:
        return "URBAN_HIGH"
    elif population_per_km2 > 1000:
        return "URBAN_MEDIUM"
    elif population_per_km2 > 200:
        return "SUBURBAN"
    else:
        return "RURAL"


def get_density_from_zip(zip_code: str, zip_density_map: dict[str, float]) -> str:
    """
    Look up density category from a zip code using a provided mapping.
    
    Args:
        zip_code: 5-digit zip code string
        zip_density_map: Dict mapping zip codes to population density
        
    Returns:
        str: Density category
    """
    density = zip_density_map.get(zip_code, 500)  # Default to suburban
    return get_density_category(density)


def normalize_input(value: str, valid_values: list[str], default: str) -> str:
    """
    Normalize and validate input values.
    
    Args:
        value: Input value to normalize
        valid_values: List of valid uppercase values
        default: Default value if input is invalid
        
    Returns:
        str: Normalized uppercase value
    """
    if value is None:
        return default
    normalized = value.upper().strip()
    return normalized if normalized in valid_values else default


# =============================================================================
# Main Prediction Function
# =============================================================================

def get_geofence_radius(
    property_type: str,
    address_source: str,
    density_category: str,
    percentile: Literal["P90", "P95", "P99"] = "P95",
    access_required: bool = False
) -> int:
    """
    Get the recommended geofence radius in meters.
    
    This function returns the optimal geofence radius based on:
    - Property type (HOUSE, APARTMENT, BUSINESS, etc.)
    - Address geocoding source (AMS, GOOGLE, MAPBOX, etc.)
    - Population density category (URBAN_HIGH, SUBURBAN, RURAL, etc.)
    - Whether access is required (gated community, buzzer, etc.)
    
    Args:
        property_type: Type of property (HOUSE, APARTMENT, BUSINESS, 
                       MOBILE_HOME, DORM, OTHER)
        address_source: Geocoding source (AMS, GOOGLE, MAPBOX, 
                        MELISSA, CUSTOMER_PIN)
        density_category: Population density (URBAN_HIGH, URBAN_MEDIUM,
                          SUBURBAN, RURAL)
        percentile: Which percentile to use (P90, P95, P99). 
                    Default is P95 (captures 95% of deliveries)
        access_required: Whether the property requires access code/buzzer.
                         Default is False. When True, radius is increased
                         based on property type (apartments +28%, etc.)
    
    Returns:
        int: Recommended geofence radius in meters
        
    Example:
        >>> get_geofence_radius("HOUSE", "AMS", "SUBURBAN")
        30
        >>> get_geofence_radius("APARTMENT", "GOOGLE", "RURAL", access_required=True)
        205
    """
    # Normalize inputs
    valid_properties = ["HOUSE", "APARTMENT", "BUSINESS", "MOBILE_HOME", "DORM", "OTHER"]
    valid_sources = ["AMS", "GOOGLE", "MAPBOX", "CUSTOMER_PIN"]
    valid_densities = ["URBAN_HIGH", "URBAN_MEDIUM", "SUBURBAN", "RURAL"]
    
    prop = normalize_input(property_type, valid_properties, "HOUSE")
    source = normalize_input(address_source, valid_sources, "AMS")
    density = normalize_input(density_category, valid_densities, "SUBURBAN")
    
    # Look up base radius (P95)
    key = (density, prop, source)
    base_radius = GEOFENCE_LOOKUP.get(key)
    
    # Fallback hierarchy
    if base_radius is None:
        # Try without source specificity
        base_radius = DEFAULT_BY_PROPERTY.get(prop, DEFAULT_RADIUS)
    
    # Apply access multiplier if access is required
    if access_required:
        access_multiplier = ACCESS_MULTIPLIERS.get(prop, 1.0)
        base_radius = base_radius * access_multiplier
    
    # Adjust for different percentiles
    if percentile == "P90":
        return int(base_radius * 0.85)  # P90 is ~15% smaller than P95
    elif percentile == "P99":
        return int(base_radius * 1.8)   # P99 is ~80% larger than P95
    else:  # P95 (default)
        return int(base_radius)


def get_arrival_radius(
    property_type: str,
    address_source: str,
    density_category: str,
    percentile: Literal["P90", "P95", "P99"] = "P95",
    access_required: bool = False
) -> int:
    """
    Get the recommended arrival radius in meters (where driver parks).
    
    This function returns the optimal arrival geofence radius based on:
    - Property type (HOUSE, APARTMENT, BUSINESS, etc.)
    - Address geocoding source (AMS, GOOGLE, MAPBOX, etc.)
    - Population density category (URBAN_HIGH, SUBURBAN, RURAL, etc.)
    - Whether access is required (gated community, buzzer, etc.)
    
    Args:
        property_type: Type of property (HOUSE, APARTMENT, BUSINESS, 
                       MOBILE_HOME, DORM, OTHER)
        address_source: Geocoding source (AMS, GOOGLE, MAPBOX, CUSTOMER_PIN)
        density_category: Population density (URBAN_HIGH, URBAN_MEDIUM,
                          SUBURBAN, RURAL)
        percentile: Which percentile to use (P90, P95, P99). 
                    Default is P95 (captures 95% of arrivals)
        access_required: Whether the property requires access code/buzzer.
                         Default is False.
    
    Returns:
        int: Recommended arrival radius in meters
        
    Example:
        >>> get_arrival_radius("HOUSE", "AMS", "SUBURBAN")
        38
        >>> get_arrival_radius("APARTMENT", "GOOGLE", "RURAL")
        164
    """
    # Normalize inputs
    valid_properties = ["HOUSE", "APARTMENT", "BUSINESS", "MOBILE_HOME", "DORM", "OTHER"]
    valid_sources = ["AMS", "GOOGLE", "MAPBOX", "CUSTOMER_PIN"]
    valid_densities = ["URBAN_HIGH", "URBAN_MEDIUM", "SUBURBAN", "RURAL"]
    
    prop = normalize_input(property_type, valid_properties, "HOUSE")
    source = normalize_input(address_source, valid_sources, "AMS")
    density = normalize_input(density_category, valid_densities, "SUBURBAN")
    
    # Look up base arrival radius (P95) - same structure as delivery lookup
    key = (density, prop, source)
    base_radius = ARRIVAL_GEOFENCE_LOOKUP.get(key)
    
    # Fallback hierarchy
    if base_radius is None:
        # Try without source specificity
        base_radius = DEFAULT_ARRIVAL_BY_PROPERTY.get(prop, 50)
    
    # Apply access multiplier if access is required (same as delivery)
    if access_required:
        access_multiplier = ACCESS_MULTIPLIERS.get(prop, 1.0)
        base_radius = base_radius * access_multiplier
    
    # Adjust for different percentiles
    if percentile == "P90":
        arrival_radius = int(base_radius * 0.85)  # P90 is ~15% smaller than P95
    elif percentile == "P99":
        arrival_radius = int(base_radius * 1.8)   # P99 is ~80% larger than P95
    else:  # P95 (default)
        arrival_radius = int(base_radius)
    
    # Ensure arrival >= delivery (driver parks at least as far as they deliver)
    # This handles edge cases like DORM/UNIVERSITY where delivery might be larger
    delivery_radius = get_geofence_radius(
        property_type=prop,
        address_source=source,
        density_category=density,
        percentile=percentile,
        access_required=access_required,
    )
    
    return max(arrival_radius, delivery_radius)


def get_geofence_radius_with_zip(
    property_type: str,
    address_source: str,
    zip_code: str,
    zip_density_map: dict[str, float],
    percentile: Literal["P90", "P95", "P99"] = "P95"
) -> int:
    """
    Get geofence radius using a zip code and density lookup table.
    
    Args:
        property_type: Type of property
        address_source: Geocoding source
        zip_code: 5-digit zip code
        zip_density_map: Dict mapping zip codes to population density (people/km²)
        percentile: Which percentile to use
        
    Returns:
        int: Recommended geofence radius in meters
    """
    density_category = get_density_from_zip(zip_code, zip_density_map)
    return get_geofence_radius(property_type, address_source, density_category, percentile)


# =============================================================================
# Batch Processing
# =============================================================================

def process_deliveries(deliveries: list[dict]) -> list[dict]:
    """
    Process a batch of deliveries and add recommended geofence radius.
    
    Args:
        deliveries: List of dicts with keys: property_type, address_source, 
                    density_category (or population_density)
                    
    Returns:
        list[dict]: Same deliveries with 'recommended_radius_m' added
    """
    results = []
    for delivery in deliveries:
        # Get density category
        if "density_category" in delivery:
            density = delivery["density_category"]
        elif "population_density" in delivery:
            density = get_density_category(delivery["population_density"])
        else:
            density = "SUBURBAN"  # Default
        
        radius = get_geofence_radius(
            property_type=delivery.get("property_type", "HOUSE"),
            address_source=delivery.get("address_source", "AMS"),
            density_category=density
        )
        
        result = {**delivery, "recommended_radius_m": radius}
        results.append(result)
    
    return results


# =============================================================================
# CLI / Demo
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 Geofence Radius Prediction Model")
    print("="*60)
    
    # Demo: Show some example predictions
    examples = [
        ("HOUSE", "AMS", "URBAN_HIGH"),
        ("HOUSE", "AMS", "RURAL"),
        ("APARTMENT", "GOOGLE", "SUBURBAN"),
        ("APARTMENT", "GOOGLE", "RURAL"),
        ("BUSINESS", "MAPBOX", "URBAN_MEDIUM"),
    ]
    
    print("\n📊 Example Predictions (P95):")
    print("-" * 60)
    print(f"{'Property':<12} {'Source':<12} {'Density':<15} {'Radius':>8}")
    print("-" * 60)
    
    for prop, source, density in examples:
        radius = get_geofence_radius(prop, source, density)
        print(f"{prop:<12} {source:<12} {density:<15} {radius:>6}m")
    
    print("\n📍 Density Category Thresholds:")
    print("  URBAN_HIGH:   > 4000 people/km²")
    print("  URBAN_MEDIUM: 1000-4000 people/km²")
    print("  SUBURBAN:     200-1000 people/km²")
    print("  RURAL:        < 200 people/km²")
    
    print("\n✅ Model ready for integration!")
    print("="*60 + "\n")
