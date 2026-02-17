/**
 * Geofence Radius Prediction Model (JavaScript Port)
 * ===================================================
 * 
 * Based on analysis of 604M delivery records
 * Source: wmt-driver-insights.Chirag_dx.geofence_delivered_distance_1yr
 * Date Range: 2025-02-10 to 2026-02-09
 * Version: 2.1.0
 * 
 * Built by Code Puppy 🐶
 */

// =============================================================================
// ARRIVAL Radius Lookup (P90, P95, P99) - Where driver parks
// =============================================================================

const ARRIVAL_LOOKUP = {
    // APARTMENT
    'APARTMENT|AMS': { P90: 45, P95: 61, P99: 125 },
    'APARTMENT|CUSTOMER_PIN': { P90: 97, P95: 167, P99: 1059 },
    'APARTMENT|DEFAULT': { P90: 308, P95: 943, P99: 5336 },
    'APARTMENT|GOOGLE': { P90: 98, P95: 147, P99: 287 },
    'APARTMENT|MANUAL_ADJ': { P90: 55, P95: 86, P99: 196 },
    'APARTMENT|MAPBOX': { P90: 97, P95: 142, P99: 278 },
    'APARTMENT|OTHER': { P90: 169, P95: 298, P99: 2721 },
    
    // BUSINESS
    'BUSINESS|AMS': { P90: 47, P95: 65, P99: 138 },
    'BUSINESS|CUSTOMER_PIN': { P90: 112, P95: 194, P99: 1435 },
    'BUSINESS|DEFAULT': { P90: 780, P95: 2346, P99: 6252 },
    'BUSINESS|GOOGLE': { P90: 102, P95: 155, P99: 342 },
    'BUSINESS|MANUAL_ADJ': { P90: 110, P95: 165, P99: 393 },
    'BUSINESS|MAPBOX': { P90: 129, P95: 190, P99: 414 },
    'BUSINESS|OTHER': { P90: 167, P95: 248, P99: 1591 },
    
    // HOUSE
    'HOUSE|AMS': { P90: 32, P95: 39, P99: 55 },
    'HOUSE|CUSTOMER_PIN': { P90: 107, P95: 239, P99: 1794 },
    'HOUSE|DEFAULT': { P90: 348, P95: 958, P99: 5735 },
    'HOUSE|GOOGLE': { P90: 48, P95: 79, P99: 192 },
    'HOUSE|MANUAL_ADJ': { P90: 40, P95: 55, P99: 141 },
    'HOUSE|MAPBOX': { P90: 52, P95: 87, P99: 214 },
    'HOUSE|OTHER': { P90: 186, P95: 391, P99: 3373 },
    
    // OTHER
    'OTHER|AMS': { P90: 43, P95: 63, P99: 154 },
    'OTHER|CUSTOMER_PIN': { P90: 133, P95: 266, P99: 1722 },
    'OTHER|DEFAULT': { P90: 1426, P95: 3874, P99: 7684 },
    'OTHER|GOOGLE': { P90: 157, P95: 240, P99: 432 },
    'OTHER|MANUAL_ADJ': { P90: 91, P95: 165, P99: 378 },
    'OTHER|MAPBOX': { P90: 171, P95: 251, P99: 500 },
    'OTHER|OTHER': { P90: 227, P95: 394, P99: 2813 },
    
    // UNIVERSITY
    'UNIVERSITY|AMS': { P90: 92, P95: 146, P99: 270 },
    'UNIVERSITY|GOOGLE': { P90: 311, P95: 402, P99: 490 },
    
    // UNKNOWN
    'UNKNOWN|AMS': { P90: 38, P95: 57, P99: 145 },
    'UNKNOWN|CUSTOMER_PIN': { P90: 218, P95: 762, P99: 5143 },
    'UNKNOWN|DEFAULT': { P90: 3598, P95: 5808, P99: 8737 },
    'UNKNOWN|MAPBOX': { P90: 90, P95: 144, P99: 343 },
    'UNKNOWN|OTHER': { P90: 56, P95: 97, P99: 387 },
};

// =============================================================================
// DELIVERY Radius Lookup (P90, P95, P99) - Where driver delivers/takes photo
// =============================================================================

const DELIVERY_LOOKUP = {
    // APARTMENT
    'APARTMENT|AMS': { P90: 27, P95: 33, P99: 62 },
    'APARTMENT|CUSTOMER_PIN': { P90: 99, P95: 171, P99: 951 },
    'APARTMENT|DEFAULT': { P90: 338, P95: 1014, P99: 5407 },
    'APARTMENT|GOOGLE': { P90: 103, P95: 154, P99: 310 },
    'APARTMENT|MANUAL_ADJ': { P90: 47, P95: 85, P99: 210 },
    'APARTMENT|MAPBOX': { P90: 108, P95: 160, P99: 327 },
    'APARTMENT|OTHER': { P90: 187, P95: 349, P99: 2810 },
    
    // BUSINESS
    'BUSINESS|AMS': { P90: 32, P95: 42, P99: 100 },
    'BUSINESS|CUSTOMER_PIN': { P90: 105, P95: 191, P99: 1728 },
    'BUSINESS|DEFAULT': { P90: 883, P95: 2494, P99: 6499 },
    'BUSINESS|GOOGLE': { P90: 101, P95: 159, P99: 423 },
    'BUSINESS|MANUAL_ADJ': { P90: 101, P95: 180, P99: 492 },
    'BUSINESS|MAPBOX': { P90: 131, P95: 204, P99: 553 },
    'BUSINESS|OTHER': { P90: 178, P95: 305, P99: 1831 },
    
    // HOUSE
    'HOUSE|AMS': { P90: 25, P95: 29, P99: 50 },
    'HOUSE|CUSTOMER_PIN': { P90: 121, P95: 276, P99: 2418 },
    'HOUSE|DEFAULT': { P90: 382, P95: 1038, P99: 5752 },
    'HOUSE|GOOGLE': { P90: 38, P95: 70, P99: 221 },
    'HOUSE|MANUAL_ADJ': { P90: 30, P95: 46, P99: 164 },
    'HOUSE|MAPBOX': { P90: 40, P95: 76, P99: 241 },
    'HOUSE|OTHER': { P90: 218, P95: 484, P99: 3551 },
    
    // OTHER
    'OTHER|AMS': { P90: 29, P95: 40, P99: 121 },
    'OTHER|CUSTOMER_PIN': { P90: 137, P95: 283, P99: 2190 },
    'OTHER|DEFAULT': { P90: 1517, P95: 3913, P99: 7725 },
    'OTHER|GOOGLE': { P90: 171, P95: 274, P99: 626 },
    'OTHER|MANUAL_ADJ': { P90: 93, P95: 181, P99: 489 },
    'OTHER|MAPBOX': { P90: 198, P95: 314, P99: 831 },
    'OTHER|OTHER': { P90: 280, P95: 483, P99: 3161 },
    
    // UNIVERSITY
    'UNIVERSITY|AMS': { P90: 66, P95: 141, P99: 359 },
    'UNIVERSITY|GOOGLE': { P90: 322, P95: 424, P99: 705 },
    
    // UNKNOWN
    'UNKNOWN|AMS': { P90: 22, P95: 30, P99: 94 },
    'UNKNOWN|CUSTOMER_PIN': { P90: 289, P95: 1246, P99: 5914 },
    'UNKNOWN|DEFAULT': { P90: 3623, P95: 5843, P99: 8739 },
    'UNKNOWN|MAPBOX': { P90: 87, P95: 143, P99: 416 },
    'UNKNOWN|OTHER': { P90: 41, P95: 83, P99: 980 },
};

// Default fallback radii by property type (P95)
const DEFAULT_ARRIVAL = {
    'HOUSE': 79,
    'APARTMENT': 147,
    'BUSINESS': 155,
    'OTHER': 240,
    'UNIVERSITY': 402,
    'UNKNOWN': 144,
};

const DEFAULT_DELIVERY = {
    'HOUSE': 70,
    'APARTMENT': 154,
    'BUSINESS': 159,
    'OTHER': 274,
    'UNIVERSITY': 424,
    'UNKNOWN': 143,
};

// Density multipliers
const DENSITY_MULTIPLIERS = {
    'URBAN_HIGH': 0.85,
    'URBAN_MEDIUM': 0.92,
    'SUBURBAN': 1.0,
    'RURAL': 1.15,
};

// Access code multipliers by property type
const ACCESS_MULTIPLIERS = {
    'APARTMENT': 1.28,
    'BUSINESS': 1.16,
    'UNIVERSITY': 1.10,
    'HOUSE': 1.01,
    'OTHER': 1.0,
    'UNKNOWN': 1.0,
};

// =============================================================================
// Main Prediction Functions
// =============================================================================

/**
 * Get the recommended ARRIVAL radius in meters (where driver parks).
 */
function getArrivalRadius(propertyType, addressSource, densityCategory, percentile = 'P95', accessRequired = false) {
    const key = `${propertyType}|${addressSource}`;
    const lookup = ARRIVAL_LOOKUP[key];
    
    let baseRadius;
    if (lookup && lookup[percentile] !== undefined) {
        baseRadius = lookup[percentile];
    } else {
        // Fallback to default
        baseRadius = DEFAULT_ARRIVAL[propertyType] || 100;
    }
    
    // Apply density multiplier
    const densityMult = DENSITY_MULTIPLIERS[densityCategory] || 1.0;
    baseRadius = baseRadius * densityMult;
    
    // Apply access multiplier
    if (accessRequired) {
        const accessMult = ACCESS_MULTIPLIERS[propertyType] || 1.0;
        baseRadius = baseRadius * accessMult;
    }
    
    // Get delivery radius to ensure arrival >= delivery
    const deliveryRadius = getDeliveryRadiusRaw(propertyType, addressSource, densityCategory, percentile, accessRequired);
    
    return Math.round(Math.max(baseRadius, deliveryRadius));
}

/**
 * Internal: Get delivery radius without the max check (to avoid recursion).
 */
function getDeliveryRadiusRaw(propertyType, addressSource, densityCategory, percentile = 'P95', accessRequired = false) {
    const key = `${propertyType}|${addressSource}`;
    const lookup = DELIVERY_LOOKUP[key];
    
    let baseRadius;
    if (lookup && lookup[percentile] !== undefined) {
        baseRadius = lookup[percentile];
    } else {
        // Fallback to default
        baseRadius = DEFAULT_DELIVERY[propertyType] || 100;
    }
    
    // Apply density multiplier
    const densityMult = DENSITY_MULTIPLIERS[densityCategory] || 1.0;
    baseRadius = baseRadius * densityMult;
    
    // Apply access multiplier
    if (accessRequired) {
        const accessMult = ACCESS_MULTIPLIERS[propertyType] || 1.0;
        baseRadius = baseRadius * accessMult;
    }
    
    return Math.round(baseRadius);
}

/**
 * Get the recommended DELIVERY radius in meters (where driver delivers/takes photo).
 */
function getGeofenceRadius(propertyType, addressSource, densityCategory, percentile = 'P95', accessRequired = false) {
    return getDeliveryRadiusRaw(propertyType, addressSource, densityCategory, percentile, accessRequired);
}

// Export for use in browser
if (typeof window !== 'undefined') {
    window.getGeofenceRadius = getGeofenceRadius;
    window.getArrivalRadius = getArrivalRadius;
    window.ARRIVAL_LOOKUP = ARRIVAL_LOOKUP;
    window.DELIVERY_LOOKUP = DELIVERY_LOOKUP;
    window.DEFAULT_ARRIVAL = DEFAULT_ARRIVAL;
    window.DEFAULT_DELIVERY = DEFAULT_DELIVERY;
}
