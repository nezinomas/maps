function initMap(routes) {
    const map = L.map(
        'map',
        { zoomControl: true, fullscreenControl: true, }
    ).setView([0, 0], 2);

    // osm layer
    const osmLayer = L.tileLayer(
        'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });

    // satellite layer
    const satelliteLayer = L.tileLayer(
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    });

    // Add OSM layer as default
    osmLayer.addTo(map);

    // Add layer control
    const baseLayers = {
        "Map": osmLayer,
        "Satellite": satelliteLayer
    };
    L.control.layers(baseLayers).addTo(map);


    // street view
    let pegmanControl = new L.Control.Pegman({
        position: 'bottomleft', // position of control inside the map
        theme: "leaflet-pegman-v3-small", // or "leaflet-pegman-v3-default"
    });
    pegmanControl.addTo(map);


    // Initialize marker cluster group
    const markers = L.markerClusterGroup({
        maxClusterRadius: 40,
        disableClusteringAtZoom: 12
    });

    const trackLayers = L.layerGroup();
    let mainPathColor = 'blue'; // Default color for the main path
    let secondaryPathColor = 'red'; // Default color for the secondary path
    let pathColor = mainPathColor; // Start with blue
    let endPoint = [0, 0]; // To store the last valid endpoint for centering

    if (routes.features && routes.features.length > 0) {
        console.log("routest", routes.features);// Set map view to the first route

        routes.features.forEach((feature, index) => {
            const coords = feature.geometry?.coordinates;
            if (!coords || !Array.isArray(coords) || coords.length === 0 || !Array.isArray(coords[0])) {
                return; // Skip this feature
            }

            // Cycle color based on last color
            const currentColor = pathColor === mainPathColor ? secondaryPathColor : mainPathColor;
            pathColor = currentColor; // Update last color for next iteration

            const trackLayer = L.geoJSON(feature, {
                style: (feature) => {
                    return {
                        color: pathColor, // Ensure valid color
                        weight: 3,
                        opacity: 0.9
                    };
                }
            });

            endPoint = feature.properties.last_point;

            let stats = feature.properties;
            console.log("stats", stats);
            let popupContent =
                `<div class="popup">` +
                `<p>${stats.date}</p>` +
                `<table>` +
                `<tr><td>Atstumas:</td><td><span>${stats.total_km || 'N/A'}</span> km</td></tr>` +
                `<tr><td>Laikas:</td><td><span>${stats.time || 'N/A'}</span> val</td></tr>` +
                `<tr><td>Vid. greitis:</td><td><span>${stats.avg_speed || 'N/A'}</span> km/h</td></tr>` +
                `<tr><td>Į kalną:</td><td><span>${stats.ascent || 'N/A'}</span> m</td></tr>` +
                `</table></div>`

            trackLayer.bindPopup(popupContent);

            const marker = L.marker(endPoint, { title: (feature.properties.name || 'Unnamed') + ' (End)' }).bindPopup(popupContent);

            markers.addLayer(marker);
            trackLayers.addLayer(trackLayer);
        });
    }
    trackLayers.addTo(map);
    map.addLayer(markers);
    map.setView(endPoint, 14);
}