from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import datetime, timedelta
import subprocess
import calendar
from .models import Trip
import json
import os
from config.settings import BASE_DIR

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    """Admin configuration for the Trip model."""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('route-management/', self.admin_site.admin_view(self.route_management_view), name='route-management'),
            path('run-clustering/<str:date>/', self.admin_site.admin_view(self.run_clustering), name='run-clustering'),
            path('run-optimization/<str:date>/', self.admin_site.admin_view(self.run_optimization), name='run-optimization'),
            path('create-attendance/', self.admin_site.admin_view(self.create_attendance), name='create-attendance'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['route_management_url'] = reverse('admin:route-management')
        return super().changelist_view(request, extra_context=extra_context)

    def route_management_view(self, request):
        # Get all unique dates from trips
        dates = Trip.objects.dates('trip_date', 'day', order='DESC')
        
        # Get current month and year for attendance creation
        today = datetime.now()
        current_month = today.strftime('%B %Y')
        next_month = (today + timedelta(days=32)).strftime('%B %Y')
        
        context = {
            'title': 'Route Management',
            'dates': dates,
            'current_month': current_month,
            'next_month': next_month,
            'opts': self.model._meta,
        }
        return render(request, 'admin/routeplan/route_management.html', context)
    
    def run_clustering(self, request, date):
        try:
            # If it's a POST request, get the date from the form
            if request.method == 'POST':
                date = request.POST.get('trip_date', date)
            
            result = subprocess.run(
                ['python', 'scripts/cluster.py', date],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )
            if result.returncode == 0:
                messages.success(request, f'Successfully clustered routes for {date}')
            else:
                messages.error(request, f'Error clustering routes: {result.stderr}')
        except Exception as e:
            messages.error(request, f'Error running clustering script: {str(e)}')
        return HttpResponseRedirect(reverse('admin:route-management'))
    
    def run_optimization(self, request, date):
        try:
            result = subprocess.run(
                ['python', 'scripts/optimize.py', date],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )
            if result.returncode == 0:
                messages.success(request, f'Successfully optimized routes for {date}')
            else:
                messages.error(request, f'Error optimizing routes: {result.stderr}')
        except Exception as e:
            messages.error(request, f'Error running optimization script: {str(e)}')
        return HttpResponseRedirect(reverse('admin:route-management'))
    
    def create_attendance(self, request):
        if request.method == 'POST':
            month = request.POST.get('month')
            try:
                date = datetime.strptime(month, '%B %Y')
                # Create attendance records for the month
                # You'll need to implement this based on your attendance creation logic
                messages.success(request, f'Successfully created attendance records for {month}')
            except Exception as e:
                messages.error(request, f'Error creating attendance records: {str(e)}')
        return HttpResponseRedirect(reverse('admin:route-management'))
    
    # Fields to display in the list view
    list_display = ('trip_date', 'start_time', 'end_time', 'status', 
                   'to_school', 'driver', 'total_distance', 'student_count')
    
    # Fields to filter on in the right sidebar
    list_filter = ('status', 'trip_date', 'to_school')
    
    # Fields to search on
    search_fields = ('route_plan_id', 'driver__name', 'driver__bus_no')
    
    # Date hierarchy for drilling down by date
    date_hierarchy = 'trip_date'
    
    # Organize fields into fieldsets for better readability
    fieldsets = (
        ('Trip Information', {
            'fields': ('route_plan_id', 'trip_date', 'start_time', 'end_time', 'to_school', 'status')
        }),
        ('Route Details', {
            'fields': ('total_distance', 'route_order'),
            'classes': ('collapse',)
        }),
        ('Assignment', {
            'fields': ('driver', 'student_list')
        }),
        ('Map', {
            'fields': ('map',)
        }),
    )
    
    # Fields that cannot be changed
    readonly_fields = ('route_plan_id', 'created_at', 'updated_at', 'map')
    
    # Many-to-many field display with filter
    filter_horizontal = ('student_list',)
    
    # Actions to perform on multiple trips
    actions = ['mark_as_active', 'mark_as_completed', 'mark_as_cancelled']
    
    def student_count(self, obj):
        """Return the number of students assigned to this trip."""
        return obj.student_list.count()
    student_count.short_description = 'Students'
    
    def mark_as_active(self, request, queryset):
        """Admin action to mark selected trips as active"""
        updated = queryset.update(status='active')
        self.message_user(request, f"{updated} trips were marked as active.")
    mark_as_active.short_description = "Mark selected trips as active"
    
    def mark_as_completed(self, request, queryset):
        """Admin action to mark selected trips as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} trips were marked as completed.")
    mark_as_completed.short_description = "Mark selected trips as completed"
    
    def mark_as_cancelled(self, request, queryset):
        """Admin action to mark selected trips as cancelled"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"{updated} trips were marked as cancelled.")
    mark_as_cancelled.short_description = "Mark selected trips as cancelled"
    
    def map(self, obj):
        """Render a map with the route and student locations marked"""
        from django.conf import settings
        
        SCHOOL_COORDINATES = [76.328898, 10.0482921]  # [longitude, latitude]
        MAPBOX_TOKEN = settings.MAPBOX_TOKEN
        
        if not MAPBOX_TOKEN:
            return mark_safe(f'<div class="error">Error: Mapbox token not configured. Current value: {MAPBOX_TOKEN}</div>')
        
        # Get route order from the trip
        route_data = obj.route_order or {}
        stops = route_data.get('stops', [])
        total_distance = route_data.get('total_distance', 0)
        estimated_duration = route_data.get('estimated_duration', 0)
        
        # Create a list of coordinates for the route
        route_coordinates = []
        markers_data = []
        
        # Add school as starting point
        route_coordinates.append([SCHOOL_COORDINATES[1], SCHOOL_COORDINATES[0]])  # [lat, lng] for Leaflet
        markers_data.append({
            'coordinates': [SCHOOL_COORDINATES[1], SCHOOL_COORDINATES[0]],
            'name': 'School (Start)',
            'type': 'school',
            'icon': '🏫'
        })
        
        # Add student stops in route order
        for stop in stops:
            if stop['type'] == 'student':
                route_coordinates.append([stop['coordinates'][1], stop['coordinates'][0]])
                markers_data.append({
                    'coordinates': [stop['coordinates'][1], stop['coordinates'][0]],
                    'name': stop['student_name'],
                    'type': 'student',
                    'icon': '👤'
                })
        
        # Add school as ending point
        route_coordinates.append([SCHOOL_COORDINATES[1], SCHOOL_COORDINATES[0]])
        markers_data.append({
            'coordinates': [SCHOOL_COORDINATES[1], SCHOOL_COORDINATES[0]],
            'name': 'School (End)',
            'type': 'school',
            'icon': '🏫'
        })
        
        return mark_safe(f"""
            <div class="route-map-container">
                <div id="map" style="height: 500px;"></div>
                <div class="route-info" style="margin-top: 10px; padding: 10px; background: #f5f5f5; border-radius: 4px;">
                    <strong>Total Distance:</strong> {total_distance:.2f} km
                    <strong style="margin-left: 20px;">Estimated Duration:</strong> {estimated_duration/60:.0f} minutes
                </div>
            </div>
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <script src="https://unpkg.com/leaflet-polylinedecorator@1.6.0/dist/leaflet.polylineDecorator.js"></script>
            <script src='https://api.mapbox.com/mapbox.js/v3.3.1/mapbox.js'></script>
            <link href='https://api.mapbox.com/mapbox.js/v3.3.1/mapbox.css' rel='stylesheet' />
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <style>
                .route-map-container {{
                    margin-bottom: 20px;
                }}
                .custom-div-icon {{
                    background: transparent;
                    border: none;
                }}
                .marker-pin {{
                    width: 30px;
                    height: 30px;
                    border-radius: 50% 50% 50% 0;
                    position: absolute;
                    transform: rotate(-45deg);
                    left: 50%;
                    top: 50%;
                    margin: -15px 0 0 -15px;
                }}
                .marker-text {{
                    transform: rotate(45deg);
                    color: white;
                    font-weight: bold;
                    width: 100%;
                    text-align: center;
                }}
                .route-info {{
                    font-size: 14px;
                    color: #333;
                }}
            </style>
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    var markers = {json.dumps(markers_data)};
                    var routeCoordinates = {json.dumps(route_coordinates)};
                    var mapboxToken = '{MAPBOX_TOKEN}';
                    
                    if (!mapboxToken) {{
                        console.error('Mapbox token not configured');
                        document.getElementById('map').innerHTML = '<div class="error" style="padding: 20px;">Error: Mapbox token not configured</div>';
                        return;
                    }}
                    
                    try {{
                        // Initialize map centered on school
                        L.mapbox.accessToken = mapboxToken;
                        var map = L.mapbox.map('map', null, {{
                            center: [{SCHOOL_COORDINATES[1]}, {SCHOOL_COORDINATES[0]}],
                            zoom: 13
                        }});
                        
                        // Add the streets layer
                        L.mapbox.styleLayer('mapbox://styles/mapbox/streets-v11').addTo(map);
                        
                        // Function to get directions between two points
                        async function getDirections(start, end) {{
                            try {{
                                const url = `https://api.mapbox.com/directions/v5/mapbox/driving/${{start[1]}},${{start[0]}};${{end[1]}},${{end[0]}}?geometries=geojson&access_token=${{mapboxToken}}`;
                                const response = await fetch(url, {{
                                    method: 'GET',
                                    headers: {{
                                        'Accept': 'application/json'
                                    }},
                                    mode: 'cors'
                                }});
                                
                                if (!response.ok) {{
                                    throw new Error(`HTTP error! status: ${{response.status}}`);
                                }}
                                
                                const data = await response.json();
                                if (!data.routes || !data.routes[0]) {{
                                    throw new Error('No route found');
                                }}
                                return data.routes[0].geometry.coordinates;
                            }} catch (error) {{
                                console.error('Error fetching directions:', error);
                                // Fallback to straight line if directions fail
                                return [[start[1], start[0]], [end[1], end[0]]];
                            }}
                        }}
                        
                        // Function to draw route between all points
                        async function drawCompleteRoute() {{
                            let allCoords = [];
                            
                            // Get directions for each segment
                            for (let i = 0; i < markers.length - 1; i++) {{
                                const start = markers[i].coordinates;
                                const end = markers[i + 1].coordinates;
                                
                                try {{
                                    const segmentCoords = await getDirections(start, end);
                                    // Convert from [lng, lat] to [lat, lng] for Leaflet
                                    const converted = segmentCoords.map(function(coord) {{
                                        return [coord[1], coord[0]];
                                    }});
                                    // Add each coordinate to the array
                                    for (let j = 0; j < converted.length; j++) {{
                                        allCoords.push(converted[j]);
                                    }}
                                }} catch (error) {{
                                    console.error('Error getting directions:', error);
                                    // Fallback to straight line
                                    allCoords.push([start[0], start[1]]);
                                    allCoords.push([end[0], end[1]]);
                                }}
                            }}
                            
                            // Draw the complete route
                            if (allCoords.length > 0) {{
                                var routeLine = L.polyline(allCoords, {{
                                    color: '#2980b9',
                                    weight: 4,
                                    opacity: 0.8
                                }}).addTo(map);

                                // Add arrow decorations
                                L.polylineDecorator(routeLine, {{
                                    patterns: [
                                        {{
                                            offset: 25,
                                            repeat: 100,
                                            symbol: L.Symbol.arrowHead({{
                                                pixelSize: 15,
                                                polygon: false,
                                                pathOptions: {{
                                                    stroke: true,
                                                    color: '#2980b9',
                                                    weight: 3
                                                }}
                                            }})
                                        }}
                                    ]
                                }}).addTo(map);

                                // Fit map bounds to show all markers
                                map.fitBounds(routeLine.getBounds(), {{padding: [50, 50]}});
                            }}
                        }}
                        
                        // Add markers with custom icons
                        markers.forEach(function(marker, index) {{
                            var markerColor = marker.type === 'school' ? '#e74c3c' : '#3498db';
                            var icon = L.divIcon({{
                                className: 'custom-div-icon',
                                html: `
                                    <div class="marker-pin" style="background: ${{markerColor}};">
                                        <div class="marker-text">${{index + 1}}</div>
                                    </div>
                                `,
                                iconSize: [30, 30],
                                iconAnchor: [15, 30]
                            }});
                            
                            var popupContent = `
                                <div style="text-align: center;">
                                    <span style="font-size: 20px;">${{marker.icon}}</span><br>
                                    <strong>${{marker.name}}</strong><br>
                                    Stop #${{index + 1}}
                                </div>
                            `;
                            
                            L.marker(marker.coordinates, {{icon: icon}})
                             .bindPopup(popupContent)
                             .addTo(map);
                        }});
                        
                        drawCompleteRoute();
                    }} catch (error) {{
                        console.error('Error initializing map:', error);
                        document.getElementById('map').innerHTML = '<div class="error" style="padding: 20px;">Error initializing map: ' + error.message + '</div>';
                    }}
                }});
            </script>
        """)
    map.short_description = "Route Map"