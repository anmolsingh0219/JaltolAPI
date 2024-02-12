# gee_api/views.py
from django.http import JsonResponse
from .utils import initialize_earth_engine
import ee
from django.conf import settings

# email = "admin-133@ee-papnejaanmol.iam.gserviceaccount.com"
# key_file = "C:/Users/papne/OneDrive/Desktop/WeLL_labs/ee-papnejaanmol-23b4363dc984.json"
# credentials = ee.ServiceAccountCredentials(email=email, key_file=key_file)

def fetch_village_analysis(request, village_name):
    # initialize_earth_engine()
    ee.Initialize()
    try:
        # Filter the VillageLevel table for Karauli villages
        village_level_table = ee.FeatureCollection("users/jaltolwelllabs/RJ_2001_2011_final_proj32644").filter(ee.Filter.eq('Dist_N_11', 'Karauli'))
        village_data = village_level_table.filter(ee.Filter.eq('name', village_name)).first()

        # Filter the ImageCollection by date range
        lulc_data = ee.ImageCollection("users/jaltolwelllabs/LULC/IndiaSAT_V2_draft").filterDate('2016-06-01', '2017-07-31')
        
        # Perform additional processing as required
        # Note: Depending on what analysis or data you want to return, you'll need to add your specific Earth Engine processing logic here

        # Example: Serialize the result for response (This is a placeholder - adapt as needed)
        serialized_data = village_data.getInfo()  # This is a basic example; adapt as per your requirements

        return JsonResponse({'data': serialized_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
# def fetch_raster_map(request, village_name):
#     ee.Initialize(credentials)
#     try:
#         # Filter the VillageLevel table for Karauli villages
#         village_level_table = ee.FeatureCollection("users/jaltolwelllabs/RJ_2001_2011_final_proj32644")
#         village_feature = village_level_table.filter(ee.Filter.eq('name', village_name)).first()

#         # Get the LULC data for the village area
#         lulc_image_collection = ee.ImageCollection("users/jaltolwelllabs/LULC/IndiaSAT_V2_draft")

#         # Select the most recent image or based on a specific date
#         lulc_image = lulc_image_collection.filterDate('2016-06-01', '2017-07-31').first()

#         # Get the visualization parameters for the LULC data
#         vis_params = {
#             'bands': ['your_band_name'],  # Replace with your specific band name
#             'min': 0,
#             'max': 12,  # Adjust the max value based on your LULC data
#             'palette': ['0000FF', '008000', '00FFFF', ...]  # Define color palette for your LULC classes
#         }

#         # Get the map ID and token for the image
#         map_id_dict = lulc_image.getMapId(vis_params)

#         # Return the map ID and token
#         return JsonResponse({
#             'mapId': map_id_dict['mapid'],
#             'token': map_id_dict['token']
#         })
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)


def karauli_villages_geojson(request):
    # initialize_earth_engine()
    ee.Initialize()
    try:
        # Fetch the Karauli village features
        village_level_table = ee.FeatureCollection("users/jaltolwelllabs/RJ_2001_2011_final_proj32644")
        karauli_villages = village_level_table.filter(ee.Filter.eq('Dist_N_11', 'Karauli'))

        # Convert features to GeoJSON
        geojson = karauli_villages.getInfo()  # This will be a dictionary that includes GeoJSON data
        
        return JsonResponse(geojson)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
 
    
def calculate_class_area(image, class_value, geometry):
    area_image = image.eq(class_value).multiply(ee.Image.pixelArea())
    area_calculation = area_image.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=geometry,
        scale=10,
        maxPixels=1e10
    )
    return area_calculation.get('b1').getInfo()

def area_change_karauli(request, village_name):
    # Initialize your Earth Engine credentials if not already initialized
    ee.Initialize()

    # Define the ImageCollection for Karauli LandUseLandCover
    image_collection = ee.ImageCollection("users/jaltolwelllabs/LULC/IndiaSAT_V2_draft")

    # Define the FeatureCollection for Karauli villages
    villages_fc = ee.FeatureCollection("users/jaltolwelllabs/RJ_2001_2011_final_proj32644").filter(
        ee.Filter.eq('Dist_N_11', 'Karauli')
    )

    # Filter the FeatureCollection for the specific village
    village_fc = villages_fc.filter(ee.Filter.eq('VCT_N_11', village_name))

    # Get the geometry for the specific village
    village_geometry = village_fc.geometry()

    # Define the labels for the classes
    class_labels = {
        '0': 'Background',
        '1': 'Built-up',
        '2': 'Water in Kharif',
        '3': 'Water in Kharif+Rabi',
        '4': 'Water in Kharif+Rabi+Zaid',
        '6': 'Tree/Forests',
        '7': 'Barrenlands',
        '8': 'Single cropping cropland',
        '9': 'Single Non-Kharif cropping cropland',
        '10': 'Double cropping cropland',
        '11': 'Triple cropping cropland',
        '12': 'Shrub_Scrub'
    }

    # Compute the area for each class over the years
    area_change_data = {}
    for year in range(2014, 2023):  # Assuming you have data from 2014 to 2022
        # Filter the ImageCollection for the specific year
        start_date = ee.Date.fromYMD(year, 6, 1)
        end_date = start_date.advance(1, 'year')
        year_image = image_collection.filterDate(start_date, end_date).mosaic()
        
        # Calculate the area for each land cover class
        for class_value, class_name in class_labels.items():
            area = calculate_class_area(year_image, int(class_value), village_geometry)
            if year not in area_change_data:
                area_change_data[year] = {}
            area_change_data[year][class_name] = area

    return JsonResponse(area_change_data)
    
    
def get_karauli_raster(request):
    ee.Initialize()
    
    try:
        # Access the ImageCollection for Karauli
        image_collection = ee.ImageCollection("users/jaltolwelllabs/LULC/IndiaSAT_V2_draft")
        
        # Here you might want to select a specific image by date or other criteria.
        # For example, to get the first image:
        image = image_collection.first()
        
        # Define visualization parameters
        vis_params = {
            'bands': ['b1'],  # Update with the correct band names
            'min': 0,
            'max': 12,
            'palette': [
                 '#b2df8a', '#6382ff', '#d7191c', '#f5ff8b', '#dcaa68',
                 '#33a02c', '#50c361', '#000000', '#dac190', '#a6cee3',
                 '#38c5f9', '#6e0002'
            ]
        }
        
        # Get the map ID and token
        map_id_dict = image.getMapId(vis_params)
        
        # Construct the tiles URL template
        tiles_url = map_id_dict['tile_fetcher'].url_format
        
        return JsonResponse({'tiles_url': tiles_url})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
