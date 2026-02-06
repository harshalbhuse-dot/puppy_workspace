"""
Geofence Radius Predictor UI
============================
A beautiful FastAPI + HTMX interface for the geofence prediction model.

Author: Code Puppy 🐶
"""

import sys
from pathlib import Path

# Add parent directory to import geofence_model
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from geofence_model import get_geofence_radius, get_arrival_radius

app = FastAPI(title="Geofence Radius Predictor", version="1.0.0")

# Templates
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Constants for dropdowns
PROPERTY_TYPES = ["HOUSE", "APARTMENT", "BUSINESS", "MOBILE_HOME", "DORM", "OTHER"]
ADDRESS_SOURCES = ["AMS", "GOOGLE", "MAPBOX", "CUSTOMER_PIN"]
DENSITY_CATEGORIES = ["URBAN_HIGH", "URBAN_MEDIUM", "SUBURBAN", "RURAL"]
PERCENTILES = ["P90", "P95", "P99"]
ACCESS_OPTIONS = ["NO", "YES"]

# Friendly labels
PROPERTY_LABELS = {
    "HOUSE": "🏠 House",
    "APARTMENT": "🏢 Apartment",
    "BUSINESS": "🏪 Business",
    "MOBILE_HOME": "🏕️ Mobile Home",
    "DORM": "🎓 Dorm",
    "OTHER": "📍 Other",
}

SOURCE_LABELS = {
    "AMS": "🎯 AMS (Most Accurate)",
    "GOOGLE": "🗺️ Google",
    "MAPBOX": "📍 Mapbox",
    "CUSTOMER_PIN": "👆 Customer Pin (Least Accurate)",
}

DENSITY_LABELS = {
    "URBAN_HIGH": "🏙️ Urban High (>4000/km²)",
    "URBAN_MEDIUM": "🌆 Urban Medium (1000-4000/km²)",
    "SUBURBAN": "🏘️ Suburban (200-1000/km²)",
    "RURAL": "🌾 Rural (<200/km²)",
}

PERCENTILE_LABELS = {
    "P90": "P90 (Tight - 90% coverage)",
    "P95": "P95 (Balanced - 95% coverage)",
    "P99": "P99 (Safe - 99% coverage)",
}

ACCESS_LABELS = {
    "NO": "🚪 No Access Required",
    "YES": "🔐 Access Required (Gate/Buzzer/Code)",
}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main UI page."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "property_types": PROPERTY_TYPES,
            "address_sources": ADDRESS_SOURCES,
            "density_categories": DENSITY_CATEGORIES,
            "percentiles": PERCENTILES,
            "property_labels": PROPERTY_LABELS,
            "source_labels": SOURCE_LABELS,
            "density_labels": DENSITY_LABELS,
            "percentile_labels": PERCENTILE_LABELS,
            "access_options": ACCESS_OPTIONS,
            "access_labels": ACCESS_LABELS,
        },
    )


@app.get("/predict", response_class=HTMLResponse)
async def predict(
    property_type: str = "HOUSE",
    address_source: str = "AMS",
    density_category: str = "SUBURBAN",
    percentile: str = "P95",
    access_required: str = "NO",
):
    """Return both arrival and delivery radius predictions as an HTMX partial."""
    access_bool = access_required.upper() == "YES"
    
    # Get both radii
    arrival_radius = get_arrival_radius(
        property_type=property_type,
        address_source=address_source,
        density_category=density_category,
        percentile=percentile,
        access_required=access_bool,
    )
    
    delivery_radius = get_geofence_radius(
        property_type=property_type,
        address_source=address_source,
        density_category=density_category,
        percentile=percentile,
        access_required=access_bool,
    )
    
    # Helper to determine styling based on radius
    def get_radius_style(radius: int) -> tuple[str, str, str]:
        if radius <= 50:
            return "text-green-600", "🎯", "Highly Accurate"
        elif radius <= 100:
            return "text-blue-600", "✅", "Good Accuracy"
        elif radius <= 200:
            return "text-yellow-600", "⚠️", "Moderate Accuracy"
        else:
            return "text-red-600", "📍", "Wide Radius"
    
    arr_color, arr_icon, arr_label = get_radius_style(arrival_radius)
    del_color, del_icon, del_label = get_radius_style(delivery_radius)
    
    return f"""
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 animate-fade-in">
        <!-- Arrival Radius -->
        <div class="bg-gray-50 rounded-xl p-6 border-2 border-gray-200">
            <div class="text-center">
                <div class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">🚗 Arrival Radius</div>
                <div class="text-xs text-gray-400 mb-4">Where driver parks</div>
                <div class="text-5xl mb-2">{arr_icon}</div>
                <div class="text-6xl font-bold {arr_color} mb-2">{arrival_radius}<span class="text-2xl">m</span></div>
                <div class="text-gray-500 text-sm">{arr_label}</div>
            </div>
        </div>
        
        <!-- Delivery Radius -->
        <div class="bg-blue-50 rounded-xl p-6 border-2 border-blue-200">
            <div class="text-center">
                <div class="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-2">📦 Delivery Radius</div>
                <div class="text-xs text-gray-400 mb-4">Where driver delivers</div>
                <div class="text-5xl mb-2">{del_icon}</div>
                <div class="text-6xl font-bold {del_color} mb-2">{delivery_radius}<span class="text-2xl">m</span></div>
                <div class="text-gray-500 text-sm">{del_label}</div>
            </div>
        </div>
    </div>
    
    <div class="mt-6 text-center text-sm text-gray-400">
        {property_type} • {address_source} • {density_category} • {percentile} • Access: {"Yes" if access_bool else "No"}
    </div>
    """


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "model": "geofence_radius_predictor"}
