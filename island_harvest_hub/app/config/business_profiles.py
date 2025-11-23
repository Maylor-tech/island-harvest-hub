"""
Business Profile Configuration

Defines all Bornfidis businesses that can be managed through the system

"""

BUSINESS_PROFILES = {
    "island_harvest": {
        "name": "Island Harvest Hub",
        "display_name": "🌴 Island Harvest Hub",
        "tagline": "Farm-to-Table Distribution • Port Antonio, Jamaica",
        "description": "Connecting local farmers with hotels and restaurants",
        "location": "Port Antonio, Jamaica",
        "primary_color": "#0B3D23",  # Bornfidis forest green
        "accent_color": "#C9A122",    # Gold
        "business_type": "distribution",
        "modules": ["customers", "suppliers", "orders", "financials", "operations", "communications"],
        "active": True
    },
    "bornfidis_provisions": {
        "name": "Bornfidis Provisions",
        "display_name": "🌱 Bornfidis Provisions",
        "tagline": "Agriculture & Food Logistics • Jamaica",
        "description": "Agricultural operations and food logistics solutions",
        "location": "Jamaica",
        "primary_color": "#0B3D23",
        "accent_color": "#C9A122",
        "business_type": "agriculture",
        "modules": ["suppliers", "inventory", "logistics", "financials", "operations"],
        "active": True
    },
    "private_chef": {
        "name": "Private Chef Services",
        "display_name": "👨‍🍳 Private Chef Services",
        "tagline": "Culinary Excellence • Okemo Valley, Vermont",
        "description": "Professional private chef services and catering",
        "location": "Okemo Valley, Vermont",
        "primary_color": "#8B4513",  # Warm brown
        "accent_color": "#C9A122",
        "business_type": "service",
        "modules": ["clients", "bookings", "menus", "financials", "communications"],
        "active": True
    },
    "bornfidis_sportswear": {
        "name": "Bornfidis Sportswear",
        "display_name": "👕 Bornfidis Sportswear",
        "tagline": "Sustainable Activewear • Jamaica & Vermont",
        "description": "Adapt, Explore, Empower - Sustainable athletic wear",
        "location": "Jamaica & Vermont",
        "primary_color": "#0B3D23",
        "accent_color": "#C9A122",
        "business_type": "retail",
        "modules": ["inventory", "orders", "customers", "financials", "ecommerce"],
        "active": True
    }
}


def get_business_profile(business_id):
    """Get a specific business profile"""
    return BUSINESS_PROFILES.get(business_id)


def get_all_active_businesses():
    """Get all active business profiles"""
    return {k: v for k, v in BUSINESS_PROFILES.items() if v.get("active", False)}


def get_business_display_names():
    """Get list of display names for dropdown"""
    return [profile["display_name"] for profile in BUSINESS_PROFILES.values() if profile.get("active", False)]

