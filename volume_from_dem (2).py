import osgeo.gdal as gdal
import osgeo.osr as osr
import numpy as np
from numpy import ma
from tqdm import tqdm
import argparse
import datetime

gdal.DontUseExceptions()

def main(file, floor, outputfile):
    start_time = datetime.datetime.now()    # get start time
    ds = gdal.OpenEx(file) # read dataset
    all_elevation_data = ds.ReadAsArray() # read elevation data into array
    gt = ds.GetGeoTransform()
    pix_width = abs(gt[1])      # size of each pixel from geotransform (width)
    pix_height = abs(gt[5])     # (height)
    ds = None # close dataset

    # VALUE TRACKING
    point_min = 10000 
    point_max = -10000
    total_vol = 0.0
    total_pixels = len(all_elevation_data) * len(all_elevation_data[0])

    # Iterate over all the data, get the values
    # compare to QGIS, seems to be accurate.
    with tqdm(total=total_pixels) as pbar:

        for row in all_elevation_data:
            
            for item in row:
                if not np.isscalar(item):
                    print("It looks like you are trying to run an RGB tif, what you need for this algorithm is a RAW tif.")
                    return 0
                pbar.update(1) # update progress bar for each pixel
                if float(item) != -9999.0:          # Seems to use -9999.0 as a "NO DATA" placeholder

                    # vol for single pixel
                    if float(item) > float(floor):
                        height_from_floor = float(item) - float(floor)
                        pix_vol = height_from_floor * pix_width * pix_width
                        total_vol += pix_vol

                    # min and max elev
                    if float(item) > point_max:
                        point_max = float(item)
                    if float(item) < point_min:
                        point_min = float(item)

    finish_time = datetime.datetime.now()       # get complete time
    outputtext = "=====================================\n"
    outputtext += "Floor set as: " + str(floor) + "\n"
    outputtext += "Input data: " + str(file) + "\n"
    outputtext += "Start time: " + str(start_time) + "\n"
    outputtext += "Finish time: " + str(finish_time) + "\n"
    outputtext += "Pixel width: " + str(pix_width) + " m\n"
    outputtext += "Pixel height: " + str(pix_height) + " m\n"
    outputtext += "Total pixels read: " + str(total_pixels) + "\n"
    outputtext += "Min elev read: " + str(point_min) + " m\n"
    outputtext += "Max elev read: " + str(point_max) + " m\n"
    outputtext += "Total calculated volume: " + str(total_vol) + " m^3\n"
    
    print(outputtext)
    if outputfile and outputfile != "":         # optionally write output to a file
        with open(outputfile, "a") as txt_file:
            txt_file.write(outputtext)

if __name__ == '__main__':
    # should use a RAW tif from WebODM, not RGB
    # should also be DSM, since we dont want the trimming that the DTM has.
    parser = argparse.ArgumentParser(description="DEM Volume Calculation")
    parser.add_argument('-d', '--dem', help='Enter a path to a RAW DEM file. Should generally be a DSM and not a DTM.', required=True, dest="dem")
    parser.add_argument('-f', '--floor', help='Enter a value (in meters) to be used as a floor for volume calculation.', required=True, dest="floor")
    parser.add_argument('-o', '--output', help='Enter a filepath to write the output to.', required=False, dest="output")
    args = parser.parse_args()

    main(args.dem, args.floor, args.output)
