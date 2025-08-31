// Map functionality for Tourism Itinerary App

let map;
let markersGroup;
let routeGroup;
let currentItinerary = null;
let stops = [];

// Map layer options
const mapLayers = {
    street: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }),
    satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: '© Esri, Maxar, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID, IGN, and the GIS User Community'
    }),
    topo: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenTopoMap (CC-BY-SA)'
    })
};

// Initialize map when document is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing map...');
    initializeMap();
    setupEventListeners();
    console.log('Map initialization complete');
});

function initializeMap() {
    // Initialize map centered on a default location (you can change this)
    map = L.map('map').setView([40.7128, -74.0060], 10); // New York City as default
    
    // Add default layer (street map)
    mapLayers.street.addTo(map);
    
    // Initialize marker and route groups
    markersGroup = L.layerGroup().addTo(map);
    routeGroup = L.layerGroup().addTo(map);
    
    // Add scale control
    L.control.scale().addTo(map);
    
    console.log('Map initialized successfully');
}

function setupEventListeners() {
    // Itinerary selection
    const itinerarySelect = document.getElementById('itinerarySelect');
    if (itinerarySelect) {
        itinerarySelect.addEventListener('change', handleItineraryChange);
    }
    
    // Map type controls
    const mapTypeControls = document.querySelectorAll('input[name="mapType"]');
    mapTypeControls.forEach(control => {
        control.addEventListener('change', handleMapTypeChange);
    });
    
    // Route type controls
    const routeTypeControls = document.querySelectorAll('input[name="routeType"]');
    routeTypeControls.forEach(control => {
        control.addEventListener('change', handleRouteTypeChange);
    });
    
    // Location and reset buttons
    const locateBtn = document.getElementById('locateBtn');
    const resetViewBtn = document.getElementById('resetViewBtn');
    
    if (locateBtn) {
        locateBtn.addEventListener('click', handleLocateUser);
    }
    
    if (resetViewBtn) {
        resetViewBtn.addEventListener('click', handleResetView);
    }
}

async function handleItineraryChange(event) {
    const itineraryId = event.target.value;
    
    if (!itineraryId) {
        clearMap();
        hideItineraryInfo();
        return;
    }
    
    try {
        // Show loading
        window.TourismApp.showLoading();
        
        // Fetch stops data
        const response = await fetch(`/api/stops/${itineraryId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch stops');
        }
        
        stops = await response.json();
        currentItinerary = itineraryId;
        
        // Display stops on map
        displayStops(stops);
        
        // Show itinerary info
        showItineraryInfo(itineraryId);
        
        // Update day progress
        updateDayProgress(stops);
        
        // Add small delay to ensure map is fully rendered, then hide loading
        setTimeout(() => {
            window.TourismApp.hideLoading();
            window.TourismApp.showAlert('Itinerary loaded successfully!', 'success');
        }, 500);
        
    } catch (error) {
        console.error('Error loading itinerary:', error);
        window.TourismApp.hideLoading();
        window.TourismApp.showAlert('Error loading itinerary. Please try again.', 'danger');
    }
}

function displayStops(stopsData) {
    // Clear existing markers and routes
    clearMap();
    
    if (!stopsData || stopsData.length === 0) {
        window.TourismApp.showAlert('No stops found for this itinerary', 'warning');
        return;
    }
    
    const coordinates = [];
    const bounds = L.latLngBounds();
    
    // Create markers for each stop
    stopsData.forEach(stop => {
        const marker = createStopMarker(stop);
        markersGroup.addLayer(marker);
        
        const latLng = L.latLng(stop.latitude, stop.longitude);
        coordinates.push(latLng);
        bounds.extend(latLng);
    });
    
    // Create route if there are multiple stops
    if (coordinates.length > 1) {
        createRoute(coordinates);
    }
    
    // Fit map to show all stops
    if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [20, 20] });
    }
}

function createStopMarker(stop) {
    const isActive = stop.is_day_active;
    const markerColor = isActive ? '#28a745' : '#6c757d';
    
    // Create custom marker
    const marker = L.circleMarker([stop.latitude, stop.longitude], {
        radius: 15,
        fillColor: markerColor,
        color: '#fff',
        weight: 3,
        opacity: 1,
        fillOpacity: 0.8,
        className: isActive ? 'active-marker' : 'inactive-marker'
    });
    
    // Add number to marker
    const icon = L.divIcon({
        html: `<div class="custom-marker ${isActive ? 'active' : 'inactive'}">${stop.order_in_day}</div>`,
        className: 'custom-div-icon',
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });
    
    const numberMarker = L.marker([stop.latitude, stop.longitude], { icon: icon });
    
    // Add click event only for active stops
    if (isActive) {
        numberMarker.on('click', () => showStopModal(stop));
        numberMarker.bindTooltip(`Day ${stop.day_number}: ${stop.name}`, {
            permanent: false,
            direction: 'top',
            offset: [0, -15]
        });
    } else {
        numberMarker.bindTooltip(`Day ${stop.day_number}: ${stop.name} (Inactive)`, {
            permanent: false,
            direction: 'top',
            offset: [0, -15]
        });
    }
    
    return numberMarker;
}

async function createRoute(coordinates) {
    if (coordinates.length < 2) return;
    
    try {
        console.log('Creating route with actual roads...');
        
        // Create route segments between consecutive stops
        for (let i = 0; i < coordinates.length - 1; i++) {
            const start = coordinates[i];
            const end = coordinates[i + 1];
            
            await createRouteSegment(start, end, i);
            
            // Add a small delay between requests to avoid rate limiting
            if (i < coordinates.length - 2) {
                await new Promise(resolve => setTimeout(resolve, 200));
            }
        }
        
    } catch (error) {
        console.error('Error creating route:', error);
        // Fallback to straight line if routing fails
        createStraightLineRoute(coordinates);
    }
}

async function createRouteSegment(start, end, segmentIndex) {
    try {
        // Get selected route type
        const routeType = document.querySelector('input[name="routeType"]:checked')?.value || 'driving';
        
        // Using OSRM (Open Source Routing Machine) - completely free, no API key required
        const osrmUrl = `https://router.project-osrm.org/route/v1/${routeType}/${start.lng},${start.lat};${end.lng},${end.lat}?overview=full&geometries=geojson&steps=true`;
        
        console.log(`Fetching route segment ${segmentIndex + 1}...`);
        
        const response = await fetch(osrmUrl);
        
        if (!response.ok) {
            throw new Error(`OSRM API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.routes && data.routes.length > 0) {
            const route = data.routes[0];
            const routeGeometry = route.geometry;
            
            // Convert coordinates from [lng, lat] to [lat, lng] for Leaflet
            const routeCoordinates = routeGeometry.coordinates.map(coord => [coord[1], coord[0]]);
            
            // Create the route polyline with a unique color for each segment
            const routePolyline = L.polyline(routeCoordinates, {
                color: getRouteColor(segmentIndex),
                weight: 5,
                opacity: 0.8,
                className: `route-segment-${segmentIndex}`
            });
            
            // Add route information
            const distance = (route.distance / 1000).toFixed(1); // Convert to km
            const duration = Math.round(route.duration / 60); // Convert to minutes
            
            // Get route type for display
            const routeType = document.querySelector('input[name="routeType"]:checked')?.value || 'driving';
            const routeIcon = routeType === 'walking' ? 'fas fa-walking' : 'fas fa-car';
            const routeText = routeType === 'walking' ? 'Walking route' : 'Driving route';
            
            routePolyline.bindPopup(`
                <div class="route-info">
                    <strong>Route Segment ${segmentIndex + 1}</strong><br>
                    <i class="fas fa-road me-1"></i> Distance: ${distance} km<br>
                    <i class="fas fa-clock me-1"></i> Duration: ${duration} min<br>
                    <i class="${routeIcon} me-1"></i> ${routeText}
                </div>
            `);
            
            routeGroup.addLayer(routePolyline);
            
            console.log(`✅ Route segment ${segmentIndex + 1} created: ${distance}km, ${duration}min`);
            
        } else {
            throw new Error('No route found in API response');
        }
        
    } catch (error) {
        console.warn(`⚠️ Failed to create route segment ${segmentIndex + 1}, using straight line:`, error.message);
        
        // Fallback to straight line for this segment
        const straightLine = L.polyline([start, end], {
            color: '#dc3545', // Red color to indicate fallback
            weight: 3,
            opacity: 0.7,
            dashArray: '10, 5'
        });
        
        straightLine.bindPopup(`
            <div class="route-info">
                <strong>Direct Path ${segmentIndex + 1}</strong><br>
                <small class="text-muted">⚠️ Road routing unavailable</small><br>
                <small class="text-muted">Showing direct line</small>
            </div>
        `);
        
        routeGroup.addLayer(straightLine);
    }
}

function createStraightLineRoute(coordinates) {
    console.log('🔄 Creating fallback straight line route');
    
    const route = L.polyline(coordinates, {
        color: '#dc3545', // Red to indicate this is a fallback
        weight: 4,
        opacity: 0.7,
        dashArray: '10, 5'
    });
    
    route.bindPopup(`
        <div class="route-info">
            <strong>Direct Path Route</strong><br>
            <small class="text-muted">⚠️ Road routing unavailable</small><br>
            <small class="text-muted">Showing straight lines between stops</small>
        </div>
    `);
    
    routeGroup.addLayer(route);
}

function getRouteColor(segmentIndex) {
    const colors = [
        '#007bff', // Blue
        '#28a745', // Green  
        '#ffc107', // Yellow
        '#dc3545', // Red
        '#6f42c1', // Purple
        '#fd7e14', // Orange
        '#20c997', // Teal
        '#e83e8c'  // Pink
    ];
    return colors[segmentIndex % colors.length];
}

function showStopModal(stop) {
    // Populate modal with stop data
    document.getElementById('stopModalTitle').textContent = stop.name;
    document.getElementById('stopDescription').textContent = stop.description || 'No description available.';
    document.getElementById('stopDayBadge').textContent = `Day ${stop.day_number}`;
    
    // Handle image
    const stopImage = document.getElementById('stopImage');
    const noImagePlaceholder = document.getElementById('noImagePlaceholder');
    
    if (stop.image_filename) {
        stopImage.src = `/static/uploads/${stop.image_filename}`;
        stopImage.style.display = 'block';
        noImagePlaceholder.style.display = 'none';
    } else {
        stopImage.style.display = 'none';
        noImagePlaceholder.style.display = 'block';
    }
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('stopModal'));
    modal.show();
}

function showItineraryInfo(itineraryId) {
    // Find the selected itinerary
    const select = document.getElementById('itinerarySelect');
    const selectedOption = select.querySelector(`option[value="${itineraryId}"]`);
    
    if (selectedOption) {
        const descriptionDiv = document.getElementById('itineraryDescription');
        const descriptionText = document.getElementById('descriptionText');
        
        // You might want to fetch full itinerary details here
        descriptionText.textContent = `Selected: ${selectedOption.textContent}`;
        descriptionDiv.style.display = 'block';
    }
}

function hideItineraryInfo() {
    const descriptionDiv = document.getElementById('itineraryDescription');
    const dayProgress = document.getElementById('dayProgress');
    
    descriptionDiv.style.display = 'none';
    dayProgress.style.display = 'none';
}

function updateDayProgress(stopsData) {
    const dayProgress = document.getElementById('dayProgress');
    const daysList = document.getElementById('daysList');
    
    if (!stopsData || stopsData.length === 0) {
        dayProgress.style.display = 'none';
        return;
    }
    
    // Get unique days and their status
    const daysMap = new Map();
    stopsData.forEach(stop => {
        if (!daysMap.has(stop.day_number)) {
            daysMap.set(stop.day_number, {
                day: stop.day_number,
                active: stop.is_day_active,
                stops: 0
            });
        }
        daysMap.get(stop.day_number).stops++;
        // If any stop is active, consider the day active
        if (stop.is_day_active) {
            daysMap.get(stop.day_number).active = true;
        }
    });
    
    // Sort days and create badges
    const days = Array.from(daysMap.values()).sort((a, b) => a.day - b.day);
    daysList.innerHTML = '';
    
    days.forEach(dayInfo => {
        const badge = document.createElement('span');
        badge.className = `day-badge ${dayInfo.active ? 'active' : 'inactive'}`;
        badge.textContent = `Day ${dayInfo.day}`;
        badge.title = `${dayInfo.stops} stops`;
        daysList.appendChild(badge);
    });
    
    dayProgress.style.display = 'block';
}

function handleMapTypeChange(event) {
    const mapType = event.target.value;
    
    // Remove all layers
    Object.values(mapLayers).forEach(layer => {
        map.removeLayer(layer);
    });
    
    // Add selected layer
    if (mapLayers[mapType]) {
        mapLayers[mapType].addTo(map);
    }
}

function handleRouteTypeChange(event) {
    console.log('Route type changed to:', event.target.value);
    
    // If an itinerary is currently loaded, recreate the routes with new type
    if (currentItinerary && stops && stops.length > 0) {
        window.TourismApp.showAlert('Updating routes...', 'info');
        
        // Clear current routes
        routeGroup.clearLayers();
        
        // Recreate routes with new type
        const coordinates = [];
        stops.forEach(stop => {
            coordinates.push(L.latLng(stop.latitude, stop.longitude));
        });
        
        if (coordinates.length > 1) {
            createRoute(coordinates);
        }
    }
}

function handleLocateUser() {
    if ('geolocation' in navigator) {
        window.TourismApp.showLoading();
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                // Add user location marker
                const userMarker = L.marker([lat, lng], {
                    icon: L.divIcon({
                        html: '<i class="fas fa-user-circle" style="color: #007bff; font-size: 24px;"></i>',
                        className: 'user-location-icon',
                        iconSize: [24, 24],
                        iconAnchor: [12, 12]
                    })
                }).bindPopup('Your Location');
                
                markersGroup.addLayer(userMarker);
                map.setView([lat, lng], 15);
                
                window.TourismApp.showAlert('Location found!', 'success');
                window.TourismApp.hideLoading();
            },
            function(error) {
                let message = 'Unable to get your location. ';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        message += 'Location access denied.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        message += 'Location information unavailable.';
                        break;
                    case error.TIMEOUT:
                        message += 'Location request timed out.';
                        break;
                }
                window.TourismApp.showAlert(message, 'warning');
                window.TourismApp.hideLoading();
            },
            { timeout: 10000, enableHighAccuracy: true }
        );
    } else {
        window.TourismApp.showAlert('Geolocation is not supported by this browser.', 'warning');
    }
}

function handleResetView() {
    if (stops && stops.length > 0) {
        // Reset to show all stops
        displayStops(stops);
    } else {
        // Reset to default view
        map.setView([40.7128, -74.0060], 10);
    }
    window.TourismApp.showAlert('Map view reset', 'info');
}

function clearMap() {
    markersGroup.clearLayers();
    routeGroup.clearLayers();
}
