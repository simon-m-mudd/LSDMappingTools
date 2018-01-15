#=============================================================================
# Script to plot chi analysis. 
#
# Authors:
#   Simon M. Mudd  
#   Fiona J. Clubb
#=============================================================================
#=============================================================================
# IMPORT MODULES
#=============================================================================
# set backend to run on server
import matplotlib
matplotlib.use('Agg')

#from __future__ import print_function
import sys
import os
from LSDPlottingTools import LSDMap_MOverNPlotting as MN
import LSDMapWrappers as LSDMW
from LSDMapFigure import PlottingHelpers as phelp


#=============================================================================
# This is just a welcome screen that is displayed if no arguments are provided.
#=============================================================================
def print_welcome():

    print("\n\n=======================================================================")
    print("Hello! I'm going to plot chi analysis results for you.")
    print("You will need to tell me which directory to look in.")
    print("Use the -dir flag to define the working directory.")
    print("If you don't do this I will assume the data is in the same directory as this script.")
    print("For help type:")
    print("   python PlotChiAnalysis.py -h\n")
    print("=======================================================================\n\n ")

#=============================================================================
# This is the main function that runs the whole thing
#=============================================================================
def main(argv):

    # If there are no arguments, send to the welcome screen
    if not len(sys.argv) > 1:
        full_paramfile = print_welcome()
        sys.exit()

    # Get the arguments
    import argparse
    parser = argparse.ArgumentParser()
    # The location of the data files
    parser.add_argument("-dir", "--base_directory", type=str, help="The base directory with the m/n analysis. If this isn't defined I'll assume it's the same as the current directory.")
    parser.add_argument("-fname", "--fname_prefix", type=str, help="The prefix of your DEM WITHOUT EXTENSION!!! This must be supplied or you will get an error (unless you're running the parallel plotting).")
    parser.add_argument("-out_fname", "--out_fname_prefix", type=str, help="The prefix of the figures WITHOUT EXTENSION!!! If not supplied the fname prefix will be used.")

    # Selecting and renaming basins
    parser.add_argument("-basin_keys", "--basin_keys",type=str,default = "", help = "This is a comma delimited string that gets the list of basins you want for the plotting. Default = no basins")  
    parser.add_argument("-rename_dict", "--rename_dict",type=str,default = "", help = "This is a string that initiates a dictionary for renaming basins. The different dict entries should be comma separated, and key and value should be separated by a colon. Default = no dict")   
     
    # What sort of analyses you want
    parser.add_argument("-PR", "--plot_rasters", type=bool, default=False, help="If this is true, I'll make raster plots of the m/n value and basin keys")
    parser.add_argument("-PCS", "--plot_chi_stack", type=bool, default=False, help="If this is true, I'll make a stack of chi plots.")


    # These control the format of your figures
    parser.add_argument("-fmt", "--FigFormat", type=str, default='png', help="Set the figure format for the plots. Default is png")
    parser.add_argument("-size", "--size_format", type=str, default='ESURF', help="Set the size format for the figure. Can be 'big' (16 inches wide), 'geomorphology' (6.25 inches wide), or 'ESURF' (4.92 inches wide) (defualt esurf).")
    parser.add_argument("-parallel", "--parallel", type=bool, default=False, help="If this is true I'll assume you ran the code in parallel and append all your CSVs together before plotting.")

    args = parser.parse_args()

    if not args.fname_prefix:
        if not args.parallel:
            print("WARNING! You haven't supplied your DEM name. Please specify this with the flag '-fname'")
            sys.exit()

    # check the basins
    print("You told me that the basin keys are: ")
    print(args.basin_keys)

    if len(args.basin_keys) == 0:
        print("No basins found, I will plot all of them")
        these_basin_keys = []
    else:
        these_basin_keys = [int(item) for item in args.basin_keys.split(',')]
        print("The basins I will plot are:")
        print(these_basin_keys)
        
    if len(args.rename_dict) == 0:
        print("No rename dictionary found. I will label with the original basin keys")
        this_rename_dict = {}
    else:
        listified_entry = [item for item in args.rename_dict.split(',')]
        this_rename_dict = {}
        
        # now loop through these creating a dict
        for entry in listified_entry:
            split_entry = entry.split(":")
            this_rename_dict[int(split_entry[0])]=split_entry[1]
            
    print("The rename dict is:")
    print(this_rename_dict)        
        

    # get the base directory
    if args.base_directory:
        this_dir = args.base_directory
        # check if you remembered a / at the end of your path_name
        if not this_dir.endswith("/"):
            print("You forgot the '/' at the end of the directory, appending...")
            this_dir = this_dir+"/"
    else:
        this_dir = os.getcwd()

        
    # See if a basin info file exists and if so get the basin list
    print("Let me check if there is a basins info csv file.")
    BasinInfoPrefix = args.fname_prefix+"_AllBasinsInfo.csv"
    BasinInfoFileName = this_dir+BasinInfoPrefix
    existing_basin_keys = []
    if os.path.isfile(BasinInfoFileName): 
        print("There is a basins info csv file")
        BasinInfoDF = phelp.ReadBasinInfoCSV(this_dir, args.fname_prefix)
        existing_basin_keys = list(BasinInfoDF['basin_key'])
        existing_basin_keys = [int(x) for x in existing_basin_keys]
    else:
        print("I didn't find a basins info csv file. Check directory or filename.")
    
    print("Let me mask get a list of the masked basins")
    
    # Python is so amazing. Look at the line below. 
    Mask_basin_keys = [i for i in existing_basin_keys if i not in these_basin_keys]
    print("All basins are: ")
    print(existing_basin_keys)
    print("The basins to keep are:")
    print(these_basin_keys)
    print("The basins to mask are:")
    print(Mask_basin_keys)
    

    # some formatting for the figures
    if args.FigFormat == "manuscipt_svg":
        print("You chose the manuscript svg option. This only works with the -ALL flag. For other flags it will default to simple svg")
        simple_format = "svg"
    elif args.FigFormat == "manuscript_png":
        print("You chose the manuscript png option. This only works with the -ALL flag. For other flags it will default to simple png")
        simple_format = "png"
    else:
        simple_format = args.FigFormat

    ChannelFname = args.fname_prefix+"_MChiSegmented.csv"
        
    # make the plots depending on your choices
    if args.plot_rasters:
        
        #LSDMW.PrintChiChannels(this_dir, args.fname_prefix, ChannelFileName = ChannelFname, add_basin_labels = True, cmap = "jet", cbar_loc = "right", size_format = "ESURF", fig_format = "png", dpi = 250,plotting_column="source_key")
        
        
        LSDMW.PrintChiChannelsAndBasins(this_dir, args.fname_prefix, ChannelFileName = ChannelFname, add_basin_labels = True, cmap = "viridis", cbar_loc = "right", size_format = "ESURF", fig_format = "png", dpi = 250,plotting_column="m_chi",colorbarlabel = "$\mathrm{log}_{10} \; \mathrm{of} \; k_{sn}$", Basin_remove_list = Mask_basin_keys, Basin_rename_dict = this_rename_dict)

        
        #MN.MakeRasterPlotsBasins(this_dir, args.fname_prefix, args.size_format, simple_format, parallel=args.parallel)
        bil = ".bil"
        
    if args.plot_chi_stack:
        
        print("I am going to plot some chi stacks gfor you.")
        LSDMW.PrintChiStacked(this_dir, args.fname_prefix, ChannelFname, cmap = "viridis", cbar_loc = "right", size_format = "ESURF", fig_format = "png", dpi = 250,plotting_column="m_chi",colorbarlabel = "$\mathrm{log}_{10} \; \mathrm{of} \; k_{sn}$",
        first_basin = 10, last_basin = 40)
    

 
 

#=============================================================================
if __name__ == "__main__":
    main(sys.argv[1:])