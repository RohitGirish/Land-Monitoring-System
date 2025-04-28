import folium
import webbrowser
import json
import os
import heapq
from random import uniform, choice
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time
import math

class IndiaLandProcurementSystem:
    def __init__(self):
        # Predefined coordinates for major Indian cities
        self.city_coordinates = {
            "Mumbai": (19.0760, 72.8777),
            "Delhi": (28.6139, 77.2090),
            "Bangalore": (12.9716, 77.5946),
            "Hyderabad": (17.3850, 78.4867),
            "Ahmedabad": (23.0225, 72.5714),
            "Chennai": (13.0827, 80.2707),
            "Kolkata": (22.5726, 88.3639),
            "Surat": (21.1702, 72.8311),
            "Pune": (18.5204, 73.8567),
            "Jaipur": (26.9124, 75.7873),
            "Lucknow": (26.8467, 80.9462),
            "Kanpur": (26.4499, 80.3319),
            "Nagpur": (21.1458, 79.0882),
            "Visakhapatnam": (17.6868, 83.2185),
            "Indore": (22.7196, 75.8577),
            "Thane": (19.2183, 72.9781),
            "Bhopal": (23.2599, 77.4126),
            "Patna": (25.5941, 85.1376),
            "Vadodara": (22.3072, 73.1812),
            "Ghaziabad": (28.6692, 77.4538)
        }
        
        self.default_city = "Delhi"
        self.geolocator = Nominatim(user_agent="india_land_system_v4", timeout=10)
        
        # Enhanced classification system
        self.classifications = {
            "govt": {
                "types": ["Central Government", "State Government", "Municipal"],
                "price_modifier": 0.7  # Government lands are typically cheaper
            },
            "public": {
                "types": ["Park", "Hospital", "School", "Transport"],
                "price_modifier": 0.9
            },
            "private": {
                "types": ["Residential", "Commercial", "Industrial", "Agricultural"],
                "price_modifier": 1.2  # Private lands are typically more expensive
            }
        }
        
        # Zone prices with additional metadata
        self.zone_prices = {
            "Central Business District": {"base_price": 150000, "radius_km": 5},
            "Residential Zone": {"base_price": 80000, "radius_km": 10},
            "Commercial Zone": {"base_price": 120000, "radius_km": 8},
            "Industrial Zone": {"base_price": 50000, "radius_km": 15},
            "Suburban": {"base_price": 40000, "radius_km": 20},
            "Rural": {"base_price": 20000, "radius_km": 30}
        }
        
        self.data_file = "india_land_data.json"
        self.land_data = {}
        self.load_data()
        
        if not self.land_data:
            self.initialize_sample_data()
    
    def load_data(self):
        """Load land data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.land_data = {tuple(eval(k)): v for k, v in data.items()}
                    print(f"Loaded {len(self.land_data)} land records")
            except Exception as e:
                print(f"Error loading data: {e}. Starting with empty dataset.")
    
    def save_data(self):
        """Save land data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump({str(k): v for k, v in self.land_data.items()}, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def haversine_distance(self, coord1, coord2):
        """Calculate distance between two coordinates in kilometers"""
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *  math.sin(dlon/2) * math.sin(dlon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def get_properties_in_radius(self, center_coord, radius_km):
        """Find properties within given radius using haversine distance"""
        properties = []
        for coord, data in self.land_data.items():
            distance = self.haversine_distance(center_coord, coord)
            if distance <= radius_km:
                properties.append((distance, coord, data))
        return properties
    
    def analyze_city_prices(self, city_name):
        """Analyze and compare land prices in a city"""
        if city_name not in self.city_coordinates:
            print(f"City {city_name} not found in database")
            return None
        
        city_center = self.city_coordinates[city_name]
        city_properties = self.get_properties_in_radius(city_center, 30)  # 30km radius
        
        if not city_properties:
            print(f"No properties found for {city_name}")
            return None
        
        # Find top 5 cheapest and most expensive properties
        cheapest = heapq.nsmallest(5, city_properties, key=lambda x: x[2]['price'])
        expensive = heapq.nlargest(5, city_properties, key=lambda x: x[2]['price'])
        
        # Calculate average price
        avg_price = sum(p[2]['price'] for p in city_properties) / len(city_properties)
        
        # Find price distribution by zone
        zone_prices = {}
        for _, _, data in city_properties:
            zone = data['zone']
            if zone not in zone_prices:
                zone_prices[zone] = []
            zone_prices[zone].append(data['price'])
        
        zone_avg = {zone: sum(prices)/len(prices) for zone, prices in zone_prices.items()}
        
        return {
            'city': city_name,
            'average_price': avg_price,
            'cheapest': cheapest,
            'most_expensive': expensive,
            'zone_prices': zone_avg
        }
    
    def geocode_city(self, city_name):
        """Get coordinates for a city"""
        if city_name in self.city_coordinates:
            return self.city_coordinates[city_name]
        
        try:
            location = self.geolocator.geocode(city_name + ", India")
            if location:
                return (location.latitude, location.longitude)
        except (GeocoderTimedOut, GeocoderUnavailable):
            pass
        
        return self.city_coordinates.get(self.default_city, (20.5937, 78.9629))
    
    def initialize_sample_data(self):
        """Create sample data for major cities"""
        print("Creating sample data...")
        for city, coords in self.city_coordinates.items():
            for i in range(10):  # 10 properties per city
                # Distribute properties in a circular pattern around the city center
                angle = uniform(0, 2 * math.pi)
                distance = uniform(0, 0.2)  # ~20km max from center
                lat = coords[0] + distance * math.cos(angle)
                lon = coords[1] + distance * math.sin(angle)
                
                main_class = choice(list(self.classifications.keys()))
                subtype = choice(self.classifications[main_class]['types'])
                zone = choice(list(self.zone_prices.keys()))
                
                # Calculate price with modifiers
                base_price = self.zone_prices[zone]['base_price']
                price_mod = self.classifications[main_class]['price_modifier']
                price = round(base_price * price_mod * uniform(0.9, 1.1), 2)
                
                self.land_data[(lat, lon)] = {
                    "city": city,
                    "address": f"Property {i+1} in {zone}, {city}",
                    "classification": main_class,
                    "subtype": subtype,
                    "zone": zone,
                    "price": price,
                    "area": round(uniform(100, 1000), 2)
                }
        self.save_data()
        print("Sample data created")
    
    def get_land_info(self, lat, lon):
        """Get land info for coordinates"""
        nearest = min(self.land_data.keys(), 
                     key=lambda p: (p[0]-lat)**2 + (p[1]-lon)**2)
        
        if (nearest[0]-lat)**2 + (nearest[1]-lon)**2 < 0.0005:
            return self.land_data[nearest]
        
        main_class = choice(list(self.classifications.keys()))
        subtype = choice(self.classifications[main_class]['types'])
        zone = choice(list(self.zone_prices.keys()))
        price_mod = self.classifications[main_class]['price_modifier']
        price = round(self.zone_prices[zone]['base_price'] * price_mod * uniform(0.8, 1.2), 2)
        
        try:
            location = self.geolocator.reverse((lat, lon), timeout=5)
            address = location.address if location else "Unknown location"
            city = self.get_city_from_address(address)
        except:
            address = "Unknown location"
            city = "Unknown"
        
        new_data = {
            "city": city,
            "address": address,
            "classification": main_class,
            "subtype": subtype,
            "zone": zone,
            "price": price,
            "area": round(uniform(100, 1000), 2)
        }
        
        self.land_data[(lat, lon)] = new_data
        self.save_data()
        return new_data
    
    def get_city_from_address(self, address):
        """Extract city name from address"""
        for city in self.city_coordinates:
            if city.lower() in address.lower():
                return city
        parts = address.split(',')
        return parts[-3].strip() if len(parts) >= 3 else "Unknown"
    
    def create_map(self, center_city, analysis_results=None):
        """Create interactive map with price analysis"""
        center_coords = self.geocode_city(center_city)
        
        self.map = folium.Map(
            location=center_coords,
            zoom_start=12,
            control_scale=True,
            tiles='cartodbpositron'
        )
        
        # Add city quick links
        city_group = folium.FeatureGroup(name="City Quick Links", show=False)
        for city, coords in self.city_coordinates.items():
            city_group.add_child(
                folium.Marker(
                    coords,
                    popup=city,
                    icon=folium.Icon(color='blue', icon='flag')
                )
            )
        self.map.add_child(city_group)
        
        # Add land markers
        self.add_land_markers()
        
        # Add price analysis markers if available
        if analysis_results:
            self.add_analysis_markers(analysis_results)
        
        # Add click handler
        self.map.add_child(folium.LatLngPopup())
        self.map.add_child(folium.ClickForMarker(popup="Loading..."))
        
        # Add layer control
        folium.LayerControl().add_to(self.map)
        
        # Save and open
        map_file = "land_map.html"
        self.map.save(map_file)
        webbrowser.open(map_file)
    
    def add_land_markers(self):
        """Add markers for land data"""
        govt = folium.FeatureGroup(name="Government")
        public = folium.FeatureGroup(name="Public")
        private = folium.FeatureGroup(name="Private")
        
        for (lat, lon), info in self.land_data.items():
            popup = f"""
            <b>{info['city']}</b><br>
            {info['address']}<br>
            Type: {info['subtype']}<br>
            Zone: {info['zone']}<br>
            Price: ₹{info['price']:,.2f}/sqm<br>
            Area: {info['area']} sqm<br>
            Total: ₹{(info['price'] * info['area']):,.2f}
            """
            
            marker = folium.Marker(
                [lat, lon],
                popup=popup,
                icon=folium.Icon(
                    color='blue' if info['classification'] == 'govt'
                    else 'green' if info['classification'] == 'public'
                    else 'red'
                )
            )
            
            if info['classification'] == 'govt':
                govt.add_child(marker)
            elif info['classification'] == 'public':
                public.add_child(marker)
            else:
                private.add_child(marker)
        
        self.map.add_child(govt)
        self.map.add_child(public)
        self.map.add_child(private)
    
    def add_analysis_markers(self, analysis):
        """Add special markers for price analysis results"""
        analysis_group = folium.FeatureGroup(name="Price Analysis", show=True)
        
        # Add cheapest properties
        for dist, coord, data in analysis['cheapest']:
            folium.Marker(
                location=coord,
                popup=f"Cheapest: ₹{data['price']:,.2f}/sqm\n{data['address']}",
                icon=folium.Icon(color='lightgreen', icon='rupee-sign', prefix='fa')
            ).add_to(analysis_group)
        
        # Add most expensive properties
        for dist, coord, data in analysis['most_expensive']:
            folium.Marker(
                location=coord,
                popup=f"Most Expensive: ₹{data['price']:,.2f}/sqm\n{data['address']}",
                icon=folium.Icon(color='darkred', icon='money-bill-wave', prefix='fa')
            ).add_to(analysis_group)
        
        # Add heatmap of prices
        price_data = []
        for coord, data in self.land_data.items():
            if data['city'].lower() == analysis['city'].lower():
                price_data.append([*coord, data['price']])
        
        if price_data:
            from folium.plugins import HeatMap
            heatmap = HeatMap(
                price_data,
                name="Price Heatmap",
                min_opacity=0.2,
                radius=15,
                blur=15,
                max_zoom=1,
            )
            self.map.add_child(heatmap)
        
        self.map.add_child(analysis_group)
        
        # Add price distribution info
        price_stats = f"""
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 300px; 
                    z-index: 9999; background: white; padding: 10px;
                    border-radius: 5px; box-shadow: 0 0 5px rgba(0,0,0,0.2)">
            <h4>Price Analysis: {analysis['city']}</h4>
            <b>Average Price:</b> ₹{analysis['average_price']:,.2f}/sqm<br>
            <b>By Zone:</b><br>
            {''.join(f"{zone}: ₹{price:,.2f}<br>" for zone, price in analysis['zone_prices'].items())}
        </div>
        """
        self.map.get_root().html.add_child(folium.Element(price_stats))

def get_user_input(prompt, default=""):
    """Get input from user with default value"""
    try:
        return input(prompt) or default
    except (EOFError, KeyboardInterrupt):
        return default

def main():
    print("\nIndia Land Procurement System with Price Analysis")
    print("===============================================")
    
    system = IndiaLandProcurementSystem()
    
    # Get user input for city
    while True:
        city = get_user_input(
            f"Enter city to analyze (default: {system.default_city}): ",
            system.default_city
        ).title()  # Convert to title case
        
        if city.lower() == 'exit':
            print("Exiting program")
            return
        
        if city in system.city_coordinates:
            break
        print(f"City not recognized. Available cities: {', '.join(system.city_coordinates.keys())}")
        print("Or type 'exit' to quit")
    
    # Analyze city prices
    print(f"\nAnalyzing land prices in {city}...")
    analysis = system.analyze_city_prices(city)
    
    if analysis:
        print("\nPrice Analysis Results:")
        print(f"Average Price: ₹{analysis['average_price']:,.2f} per sqm")
        print("\nCheapest Properties:")
        for dist, coord, data in analysis['cheapest']:
            print(f"- ₹{data['price']:,.2f}/sqm: {data['address']} ({dist:.1f}km from center)")
        
        print("\nMost Expensive Properties:")
        for dist, coord, data in analysis['most_expensive']:
            print(f"- ₹{data['price']:,.2f}/sqm: {data['address']} ({dist:.1f}km from center)")
        
        print("\nAverage Prices by Zone:")
        for zone, price in analysis['zone_prices'].items():
            print(f"- {zone}: ₹{price:,.2f}/sqm")
    
    # Create map with analysis results
    system.create_map(city, analysis)
    
    print("\nMap opened in browser with price analysis:")
    print("- Green markers: Cheapest properties")
    print("- Red markers: Most expensive properties")
    print("- Heatmap shows price distribution")
    print("- Price stats shown in bottom-left corner")
    print("- Use layer control (top-right) to toggle features")

if __name__ == "__main__":
    main()