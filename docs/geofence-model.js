/**
 * Geofence Radius Prediction Model (JavaScript Port)
 * ===================================================
 * 
 * A simple, production-ready lookup module for predicting optimal geofence
 * radii based on property type, address source, and population density.
 * 
 * Based on analysis of 26.8M delivery records from Chirag_dx.20250501_dlvrd_distance
 * 
 * Ported from Python by Code Puppy 🐶
 */

// =============================================================================
// Geofence Lookup Table (P95 Percentile - captures 95% of deliveries)
// =============================================================================

const GEOFENCE_LOOKUP = {
    // URBAN_HIGH (>4000 people/km²)
    'URBAN_HIGH|HOUSE|AMS': 28,
    'URBAN_HIGH|HOUSE|GOOGLE': 70,
    'URBAN_HIGH|HOUSE|MAPBOX': 85,
    'URBAN_HIGH|HOUSE|CUSTOMER_PIN': 400,
    'URBAN_HIGH|APARTMENT|AMS': 45,
    'URBAN_HIGH|APARTMENT|GOOGLE': 140,
    'URBAN_HIGH|APARTMENT|MAPBOX': 150,
    'URBAN_HIGH|APARTMENT|CUSTOMER_PIN': 450,
    'URBAN_HIGH|BUSINESS|AMS': 48,
    'URBAN_HIGH|BUSINESS|GOOGLE': 100,
    'URBAN_HIGH|BUSINESS|MAPBOX': 120,
    'URBAN_HIGH|BUSINESS|CUSTOMER_PIN': 400,
    'URBAN_HIGH|MOBILE_HOME|AMS': 25,
    'URBAN_HIGH|MOBILE_HOME|GOOGLE': 70,
    'URBAN_HIGH|MOBILE_HOME|MAPBOX': 80,
    'URBAN_HIGH|MOBILE_HOME|CUSTOMER_PIN': 400,
    'URBAN_HIGH|DORM|AMS': 200,
    'URBAN_HIGH|DORM|GOOGLE': 220,
    'URBAN_HIGH|DORM|MAPBOX': 230,
    'URBAN_HIGH|DORM|CUSTOMER_PIN': 500,
    'URBAN_HIGH|OTHER|AMS': 70,
    'URBAN_HIGH|OTHER|GOOGLE': 120,
    'URBAN_HIGH|OTHER|MAPBOX': 130,
    'URBAN_HIGH|OTHER|CUSTOMER_PIN': 450,
    
    // URBAN_MEDIUM (1000-4000 people/km²)
    'URBAN_MEDIUM|HOUSE|AMS': 29,
    'URBAN_MEDIUM|HOUSE|GOOGLE': 72,
    'URBAN_MEDIUM|HOUSE|MAPBOX': 88,
    'URBAN_MEDIUM|HOUSE|CUSTOMER_PIN': 420,
    'URBAN_MEDIUM|APARTMENT|AMS': 45,
    'URBAN_MEDIUM|APARTMENT|GOOGLE': 145,
    'URBAN_MEDIUM|APARTMENT|MAPBOX': 155,
    'URBAN_MEDIUM|APARTMENT|CUSTOMER_PIN': 480,
    'URBAN_MEDIUM|BUSINESS|AMS': 50,
    'URBAN_MEDIUM|BUSINESS|GOOGLE': 100,
    'URBAN_MEDIUM|BUSINESS|MAPBOX': 120,
    'URBAN_MEDIUM|BUSINESS|CUSTOMER_PIN': 420,
    'URBAN_MEDIUM|MOBILE_HOME|AMS': 26,
    'URBAN_MEDIUM|MOBILE_HOME|GOOGLE': 72,
    'URBAN_MEDIUM|MOBILE_HOME|MAPBOX': 82,
    'URBAN_MEDIUM|MOBILE_HOME|CUSTOMER_PIN': 420,
    'URBAN_MEDIUM|DORM|AMS': 210,
    'URBAN_MEDIUM|DORM|GOOGLE': 225,
    'URBAN_MEDIUM|DORM|MAPBOX': 235,
    'URBAN_MEDIUM|DORM|CUSTOMER_PIN': 520,
    'URBAN_MEDIUM|OTHER|AMS': 72,
    'URBAN_MEDIUM|OTHER|GOOGLE': 125,
    'URBAN_MEDIUM|OTHER|MAPBOX': 135,
    'URBAN_MEDIUM|OTHER|CUSTOMER_PIN': 470,
    
    // SUBURBAN (200-1000 people/km²)
    'SUBURBAN|HOUSE|AMS': 30,
    'SUBURBAN|HOUSE|GOOGLE': 75,
    'SUBURBAN|HOUSE|MAPBOX': 90,
    'SUBURBAN|HOUSE|CUSTOMER_PIN': 450,
    'SUBURBAN|APARTMENT|AMS': 40,
    'SUBURBAN|APARTMENT|GOOGLE': 130,
    'SUBURBAN|APARTMENT|MAPBOX': 140,
    'SUBURBAN|APARTMENT|CUSTOMER_PIN': 500,
    'SUBURBAN|BUSINESS|AMS': 50,
    'SUBURBAN|BUSINESS|GOOGLE': 100,
    'SUBURBAN|BUSINESS|MAPBOX': 120,
    'SUBURBAN|BUSINESS|CUSTOMER_PIN': 450,
    'SUBURBAN|MOBILE_HOME|AMS': 28,
    'SUBURBAN|MOBILE_HOME|GOOGLE': 75,
    'SUBURBAN|MOBILE_HOME|MAPBOX': 85,
    'SUBURBAN|MOBILE_HOME|CUSTOMER_PIN': 450,
    'SUBURBAN|DORM|AMS': 216,
    'SUBURBAN|DORM|GOOGLE': 230,
    'SUBURBAN|DORM|MAPBOX': 240,
    'SUBURBAN|DORM|CUSTOMER_PIN': 550,
    'SUBURBAN|OTHER|AMS': 75,
    'SUBURBAN|OTHER|GOOGLE': 130,
    'SUBURBAN|OTHER|MAPBOX': 140,
    'SUBURBAN|OTHER|CUSTOMER_PIN': 500,
    
    // RURAL (<200 people/km²)
    'RURAL|HOUSE|AMS': 34,
    'RURAL|HOUSE|GOOGLE': 80,
    'RURAL|HOUSE|MAPBOX': 95,
    'RURAL|HOUSE|CUSTOMER_PIN': 500,
    'RURAL|APARTMENT|AMS': 50,
    'RURAL|APARTMENT|GOOGLE': 160,
    'RURAL|APARTMENT|MAPBOX': 170,
    'RURAL|APARTMENT|CUSTOMER_PIN': 550,
    'RURAL|BUSINESS|AMS': 55,
    'RURAL|BUSINESS|GOOGLE': 110,
    'RURAL|BUSINESS|MAPBOX': 130,
    'RURAL|BUSINESS|CUSTOMER_PIN': 500,
    'RURAL|MOBILE_HOME|AMS': 30,
    'RURAL|MOBILE_HOME|GOOGLE': 80,
    'RURAL|MOBILE_HOME|MAPBOX': 90,
    'RURAL|MOBILE_HOME|CUSTOMER_PIN': 500,
    'RURAL|DORM|AMS': 220,
    'RURAL|DORM|GOOGLE': 240,
    'RURAL|DORM|MAPBOX': 250,
    'RURAL|DORM|CUSTOMER_PIN': 600,
    'RURAL|OTHER|AMS': 80,
    'RURAL|OTHER|GOOGLE': 140,
    'RURAL|OTHER|MAPBOX': 150,
    'RURAL|OTHER|CUSTOMER_PIN': 550,
};

// =============================================================================
// Arrival Radius Lookup Table (P95 Percentile - where driver parks)
// =============================================================================

const ARRIVAL_GEOFENCE_LOOKUP = {
    // URBAN_HIGH (>4000 people/km²)
    'URBAN_HIGH|HOUSE|AMS': 36,
    'URBAN_HIGH|HOUSE|GOOGLE': 50,
    'URBAN_HIGH|HOUSE|MAPBOX': 55,
    'URBAN_HIGH|HOUSE|CUSTOMER_PIN': 138,
    'URBAN_HIGH|APARTMENT|AMS': 69,
    'URBAN_HIGH|APARTMENT|GOOGLE': 92,
    'URBAN_HIGH|APARTMENT|MAPBOX': 86,
    'URBAN_HIGH|APARTMENT|CUSTOMER_PIN': 107,
    'URBAN_HIGH|BUSINESS|AMS': 65,
    'URBAN_HIGH|BUSINESS|GOOGLE': 114,
    'URBAN_HIGH|BUSINESS|MAPBOX': 100,
    'URBAN_HIGH|BUSINESS|CUSTOMER_PIN': 200,
    'URBAN_HIGH|MOBILE_HOME|AMS': 36,
    'URBAN_HIGH|MOBILE_HOME|GOOGLE': 50,
    'URBAN_HIGH|MOBILE_HOME|MAPBOX': 55,
    'URBAN_HIGH|MOBILE_HOME|CUSTOMER_PIN': 138,
    'URBAN_HIGH|DORM|AMS': 91,
    'URBAN_HIGH|DORM|GOOGLE': 138,
    'URBAN_HIGH|DORM|MAPBOX': 150,
    'URBAN_HIGH|DORM|CUSTOMER_PIN': 200,
    'URBAN_HIGH|OTHER|AMS': 64,
    'URBAN_HIGH|OTHER|GOOGLE': 138,
    'URBAN_HIGH|OTHER|MAPBOX': 120,
    'URBAN_HIGH|OTHER|CUSTOMER_PIN': 200,
    
    // URBAN_MEDIUM (1000-4000 people/km²)
    'URBAN_MEDIUM|HOUSE|AMS': 35,
    'URBAN_MEDIUM|HOUSE|GOOGLE': 51,
    'URBAN_MEDIUM|HOUSE|MAPBOX': 52,
    'URBAN_MEDIUM|HOUSE|CUSTOMER_PIN': 144,
    'URBAN_MEDIUM|APARTMENT|AMS': 68,
    'URBAN_MEDIUM|APARTMENT|GOOGLE': 152,
    'URBAN_MEDIUM|APARTMENT|MAPBOX': 127,
    'URBAN_MEDIUM|APARTMENT|CUSTOMER_PIN': 183,
    'URBAN_MEDIUM|BUSINESS|AMS': 64,
    'URBAN_MEDIUM|BUSINESS|GOOGLE': 143,
    'URBAN_MEDIUM|BUSINESS|MAPBOX': 119,
    'URBAN_MEDIUM|BUSINESS|CUSTOMER_PIN': 188,
    'URBAN_MEDIUM|MOBILE_HOME|AMS': 35,
    'URBAN_MEDIUM|MOBILE_HOME|GOOGLE': 51,
    'URBAN_MEDIUM|MOBILE_HOME|MAPBOX': 52,
    'URBAN_MEDIUM|MOBILE_HOME|CUSTOMER_PIN': 144,
    'URBAN_MEDIUM|DORM|AMS': 91,
    'URBAN_MEDIUM|DORM|GOOGLE': 180,
    'URBAN_MEDIUM|DORM|MAPBOX': 185,
    'URBAN_MEDIUM|DORM|CUSTOMER_PIN': 244,
    'URBAN_MEDIUM|OTHER|AMS': 60,
    'URBAN_MEDIUM|OTHER|GOOGLE': 180,
    'URBAN_MEDIUM|OTHER|MAPBOX': 185,
    'URBAN_MEDIUM|OTHER|CUSTOMER_PIN': 244,
    
    // SUBURBAN (200-1000 people/km²)
    'SUBURBAN|HOUSE|AMS': 38,
    'SUBURBAN|HOUSE|GOOGLE': 59,
    'SUBURBAN|HOUSE|MAPBOX': 58,
    'SUBURBAN|HOUSE|CUSTOMER_PIN': 244,
    'SUBURBAN|APARTMENT|AMS': 60,
    'SUBURBAN|APARTMENT|GOOGLE': 176,
    'SUBURBAN|APARTMENT|MAPBOX': 150,
    'SUBURBAN|APARTMENT|CUSTOMER_PIN': 232,
    'SUBURBAN|BUSINESS|AMS': 65,
    'SUBURBAN|BUSINESS|GOOGLE': 168,
    'SUBURBAN|BUSINESS|MAPBOX': 176,
    'SUBURBAN|BUSINESS|CUSTOMER_PIN': 266,
    'SUBURBAN|MOBILE_HOME|AMS': 38,
    'SUBURBAN|MOBILE_HOME|GOOGLE': 59,
    'SUBURBAN|MOBILE_HOME|MAPBOX': 58,
    'SUBURBAN|MOBILE_HOME|CUSTOMER_PIN': 244,
    'SUBURBAN|DORM|AMS': 91,
    'SUBURBAN|DORM|GOOGLE': 253,
    'SUBURBAN|DORM|MAPBOX': 201,
    'SUBURBAN|DORM|CUSTOMER_PIN': 426,
    'SUBURBAN|OTHER|AMS': 62,
    'SUBURBAN|OTHER|GOOGLE': 253,
    'SUBURBAN|OTHER|MAPBOX': 201,
    'SUBURBAN|OTHER|CUSTOMER_PIN': 426,
    
    // RURAL (<200 people/km²)
    'RURAL|HOUSE|AMS': 42,
    'RURAL|HOUSE|GOOGLE': 110,
    'RURAL|HOUSE|MAPBOX': 119,
    'RURAL|HOUSE|CUSTOMER_PIN': 763,
    'RURAL|APARTMENT|AMS': 57,
    'RURAL|APARTMENT|GOOGLE': 164,
    'RURAL|APARTMENT|MAPBOX': 144,
    'RURAL|APARTMENT|CUSTOMER_PIN': 345,
    'RURAL|BUSINESS|AMS': 69,
    'RURAL|BUSINESS|GOOGLE': 196,
    'RURAL|BUSINESS|MAPBOX': 250,
    'RURAL|BUSINESS|CUSTOMER_PIN': 529,
    'RURAL|MOBILE_HOME|AMS': 42,
    'RURAL|MOBILE_HOME|GOOGLE': 110,
    'RURAL|MOBILE_HOME|MAPBOX': 119,
    'RURAL|MOBILE_HOME|CUSTOMER_PIN': 763,
    'RURAL|DORM|AMS': 91,
    'RURAL|DORM|GOOGLE': 294,
    'RURAL|DORM|MAPBOX': 302,
    'RURAL|DORM|CUSTOMER_PIN': 1014,
    'RURAL|OTHER|AMS': 73,
    'RURAL|OTHER|GOOGLE': 294,
    'RURAL|OTHER|MAPBOX': 302,
    'RURAL|OTHER|CUSTOMER_PIN': 1014,
};

// Default fallback radii by property type
const DEFAULT_BY_PROPERTY = {
    'HOUSE': 50,
    'APARTMENT': 85,
    'BUSINESS': 75,
    'MOBILE_HOME': 45,
    'DORM': 220,
    'OTHER': 100,
};

const DEFAULT_ARRIVAL_BY_PROPERTY = {
    'HOUSE': 50,
    'APARTMENT': 80,
    'BUSINESS': 80,
    'MOBILE_HOME': 50,
    'DORM': 150,
    'OTHER': 80,
};

// Access code multipliers by property type
const ACCESS_MULTIPLIERS = {
    'APARTMENT': 1.28,
    'BUSINESS': 1.16,
    'DORM': 1.10,
    'HOUSE': 1.01,
    'MOBILE_HOME': 1.0,
    'OTHER': 1.0,
};

// =============================================================================
// Main Prediction Functions
// =============================================================================

/**
 * Get the recommended delivery geofence radius in meters.
 */
function getGeofenceRadius(propertyType, addressSource, densityCategory, percentile = 'P95', accessRequired = false) {
    const key = `${densityCategory}|${propertyType}|${addressSource}`;
    let baseRadius = GEOFENCE_LOOKUP[key];
    
    // Fallback
    if (baseRadius === undefined) {
        baseRadius = DEFAULT_BY_PROPERTY[propertyType] || 50;
    }
    
    // Apply access multiplier
    if (accessRequired) {
        const multiplier = ACCESS_MULTIPLIERS[propertyType] || 1.0;
        baseRadius = baseRadius * multiplier;
    }
    
    // Adjust for percentile
    if (percentile === 'P90') {
        return Math.round(baseRadius * 0.85);
    } else if (percentile === 'P99') {
        return Math.round(baseRadius * 1.8);
    }
    return Math.round(baseRadius);
}

/**
 * Get the recommended arrival radius in meters (where driver parks).
 */
function getArrivalRadius(propertyType, addressSource, densityCategory, percentile = 'P95', accessRequired = false) {
    const key = `${densityCategory}|${propertyType}|${addressSource}`;
    let baseRadius = ARRIVAL_GEOFENCE_LOOKUP[key];
    
    // Fallback
    if (baseRadius === undefined) {
        baseRadius = DEFAULT_ARRIVAL_BY_PROPERTY[propertyType] || 50;
    }
    
    // Apply access multiplier
    if (accessRequired) {
        const multiplier = ACCESS_MULTIPLIERS[propertyType] || 1.0;
        baseRadius = baseRadius * multiplier;
    }
    
    // Adjust for percentile
    let arrivalRadius;
    if (percentile === 'P90') {
        arrivalRadius = Math.round(baseRadius * 0.85);
    } else if (percentile === 'P99') {
        arrivalRadius = Math.round(baseRadius * 1.8);
    } else {
        arrivalRadius = Math.round(baseRadius);
    }
    
    // Ensure arrival >= delivery
    const deliveryRadius = getGeofenceRadius(propertyType, addressSource, densityCategory, percentile, accessRequired);
    return Math.max(arrivalRadius, deliveryRadius);
}
