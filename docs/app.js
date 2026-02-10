/**
 * Geofence Radius Predictor - UI Logic
 * =====================================
 * 
 * Handles form changes and updates the result display.
 * 
 * Built by Code Puppy 🐶
 */

// Get radius styling based on value
function getRadiusStyle(radius) {
    if (radius <= 50) {
        return { color: 'text-green-600', icon: '🎯', label: 'Highly Accurate' };
    } else if (radius <= 100) {
        return { color: 'text-blue-600', icon: '✅', label: 'Good Accuracy' };
    } else if (radius <= 200) {
        return { color: 'text-yellow-600', icon: '⚠️', label: 'Moderate Accuracy' };
    } else {
        return { color: 'text-red-600', icon: '📍', label: 'Wide Radius' };
    }
}

// Update the result display
function updateResult() {
    const form = document.getElementById('predictForm');
    const resultDiv = document.getElementById('result');
    
    // Get form values
    const propertyType = form.property_type.value;
    const addressSource = form.address_source.value;
    const densityCategory = form.density_category.value;
    const percentile = form.percentile.value;
    const accessRequired = form.access_required.value === 'YES';
    
    // Calculate radii
    const arrivalRadius = getArrivalRadius(propertyType, addressSource, densityCategory, percentile, accessRequired);
    const deliveryRadius = getGeofenceRadius(propertyType, addressSource, densityCategory, percentile, accessRequired);
    
    // Get styling
    const arrStyle = getRadiusStyle(arrivalRadius);
    const delStyle = getRadiusStyle(deliveryRadius);
    
    // Build result HTML
    resultDiv.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 animate-fade-in">
            <!-- Arrival Radius -->
            <div class="bg-gray-50 rounded-xl p-6 border-2 border-gray-200">
                <div class="text-center">
                    <div class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">🚗 Arrival Radius</div>
                    <div class="text-xs text-gray-400 mb-4">Where driver parks</div>
                    <div class="text-5xl mb-2">${arrStyle.icon}</div>
                    <div class="text-6xl font-bold ${arrStyle.color} mb-2">${arrivalRadius}<span class="text-2xl">m</span></div>
                    <div class="text-gray-500 text-sm">${arrStyle.label}</div>
                </div>
            </div>
            
            <!-- Delivery Radius -->
            <div class="bg-blue-50 rounded-xl p-6 border-2 border-blue-200">
                <div class="text-center">
                    <div class="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-2">📦 Delivery Radius</div>
                    <div class="text-xs text-gray-400 mb-4">Where driver delivers</div>
                    <div class="text-5xl mb-2">${delStyle.icon}</div>
                    <div class="text-6xl font-bold ${delStyle.color} mb-2">${deliveryRadius}<span class="text-2xl">m</span></div>
                    <div class="text-gray-500 text-sm">${delStyle.label}</div>
                </div>
            </div>
        </div>
        
        <div class="mt-6 text-center text-sm text-gray-400">
            ${propertyType} • ${addressSource} • ${densityCategory} • ${percentile} • Access: ${accessRequired ? 'Yes' : 'No'}
        </div>
    `;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictForm');
    
    // Update on any form change
    form.addEventListener('change', updateResult);
    
    // Initial calculation
    updateResult();
});
