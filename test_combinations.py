"""Test ALL combinations for arrival >= delivery including access & percentiles"""
from geofence_model import get_geofence_radius, get_arrival_radius

properties = ['HOUSE', 'APARTMENT', 'BUSINESS', 'MOBILE_HOME', 'DORM', 'OTHER']
sources = ['AMS', 'GOOGLE', 'MAPBOX', 'CUSTOMER_PIN']
densities = ['URBAN_HIGH', 'URBAN_MEDIUM', 'SUBURBAN', 'RURAL']
percentiles = ['P90', 'P95', 'P99']
access_options = [False, True]

issues = []
total = 0

for prop in properties:
    for source in sources:
        for density in densities:
            for percentile in percentiles:
                for access in access_options:
                    total += 1
                    arr = get_arrival_radius(prop, source, density, percentile, access)
                    dlv = get_geofence_radius(prop, source, density, percentile, access)
                    if arr < dlv:
                        issues.append((prop, source, density, percentile, access, arr, dlv))

print(f'Tested {total} combinations')
print(f'Found {len(issues)} issues where Arrival < Delivery:')
print()

if issues:
    print('Property      | Source       | Density       | Pctl | Access | Arrival | Delivery')
    print('-' * 85)
    for prop, source, density, pctl, access, arr, dlv in issues:
        acc_str = 'Yes' if access else 'No'
        print(f'{prop:13} | {source:12} | {density:13} | {pctl:4} | {acc_str:6} | {arr:7}m | {dlv:7}m')
else:
    print('All combinations pass! Arrival >= Delivery everywhere.')
