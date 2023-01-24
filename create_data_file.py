import pandas as pd
import os
from pathlib import Path

data_folder = os.path.join(os.getcwd(), "..", "raw_data")

def depression_data():
    """
    Subsets the depression data file to only the depression data for DC and PG County, MD
    INPUT: None, but expects data file to already exist: `raw_data/depression_census_tract_data.csv`
    OUTPUT: Dataframe with depression rate for DC and P.G. County census tracts

    Data source: https://chronicdata.cdc.gov/500-Cities-Places/PLACES-Local-Data-for-Better-Health-Place-Data-202/eav7-hnsx
    """
    print("\n~*~*~*~*~*~*~*~* Cleaning depression data ~*~*~*~*~*~*~*~*")
    # file_name = 'PLACES__Local_Data_for_Better_Health__Census_Tract_Data_2022_release.csv'
    file_name = 'depression_census_tract_data.csv'
    file_path_name = os.path.join(data_folder, file_name)

    try:
        all_tracts_df = pd.read_csv(file_path_name)
    except:
        while not os.path.exists(file_path_name):
            input("Visit https://chronicdata.cdc.gov/500-Cities-Places/PLACES-Local-Data-for-Better-Health-Place-Data-202/eav7-hnsx\n"+
                "and save the file at the census tract level with file name `depression_census_tract_data.csv`\n"+
                "in the `raw_data` folder located above this folder.\n"+
                "Press `enter` when finished.")
            all_tracts_df = pd.read_csv(file_path_name)

    # ----- SET ALL THE FILTERS THAT WE'LL APPLY TO THE DATA -----
    md_filter = (all_tracts_df['StateAbbr']=='MD') & (all_tracts_df['CountyName']=="Prince George's")
    dc_filter = (all_tracts_df['StateAbbr']=='DC')
    location_filter = (md_filter | dc_filter)
    measure_filter = (all_tracts_df.Measure.str.contains('Depress'))
    # set the subset year (we eventually want to make this more dynamic in future iterations)
    subset_year = 2020
    year_filter = (all_tracts_df.Year == subset_year)

    # subset this to depression data for DC and PG county Maryland
    depression_data = all_tracts_df[year_filter & location_filter & measure_filter].copy(deep=True)

    # convert LocationID so that it's a string
    depression_data['LocationID'] = depression_data['LocationID'].astype(str)

    # sanity check; print lines for status report
    print("Number of census tracts with depression data:", len(depression_data))
    print("Counties pulled for depression data:", depression_data.CountyName.unique())
    
    # return cleaned dataframe
    return(depression_data)

def walkability_data():
    """
    Aggregates a Walkability score for each census tract by getting the median score across census blocks.
    INPUT: None, but expects data file to already exist: `raw_data/walkability_census_block_data.csv`
    OUTPUT: Dataframe with median walkability score for each census tract in America.
    """
    print("\n~*~*~*~*~*~*~*~* Cleaning walkability data ~*~*~*~*~*~*~*~*")
    file_name = 'walkability_census_block_data.csv'
    file_path_name = os.path.join(data_folder, file_name)

    try:
        walk_score = pd.read_csv(file_path_name)
    except:
        while not os.path.exists(file_path_name):
            input("Visit https://catalog.data.gov/dataset/walkability-index\n"+
                "and save the file with file name `walkability_census_block_data.csv`\n"+
                "in the `raw_data` folder located above this folder.\n"+
                "Press `enter` when finished.")
            walk_score = pd.read_csv(file_path_name)

    # define cols to keep
    cols_keep = ['OBJECTID',
                'GEOID10',
                'GEOID20',
                'STATEFP',
                'COUNTYFP',
                'TRACTCE',
                'BLKGRPCE',
                'CSA',
                'CSA_Name',
                'CBSA',
                'CBSA_Name',
                'NatWalkInd']
    walk_score = walk_score[cols_keep].copy(deep=True)

    # create the location id aka census tract id by concatenating state, county, and tract
    walk_score['location_id'] = walk_score['STATEFP'].astype(str).str.zfill(2) + walk_score['COUNTYFP'].astype(str).str.zfill(3) + walk_score['TRACTCE'].astype(str).str.zfill(6)
    # group by census tracts
    median_walk_by_tract = walk_score.groupby(["location_id"])["NatWalkInd"].median().reset_index().rename({'NatWalkInd':'Median_NatWalkInd'}, axis='columns')
    mean_walk_by_tract = walk_score.groupby(["location_id"])["NatWalkInd"].mean().reset_index().rename({'NatWalkInd':'Mean_NatWalkInd'}, axis='columns')

    # return cleaned dataframe
    return(median_walk_by_tract)

def cre_equity_data():
    """
    Subsets the CRE Equity Supplement file to just the columns of interest (as defined by SWT)
    INPUT: None, but expects data file to already exist: `raw_data/cre_equity_census_tract_data.csv`
    OUTPUT: Dataframe with CRE Equity Risk Factor Scores for each census tract in America.
    """
    print("\n~*~*~*~*~*~*~*~* Cleaning CRE Equity data ~*~*~*~*~*~*~*~*")
    file_name = 'cre_equity_census_tract_data.csv'
    file_path_name = os.path.join(data_folder, file_name)
    cre_equity = None

    try:
        cre_equity = pd.read_csv(file_path_name, encoding='latin1')
    except:
        while not os.path.exists(file_path_name):
            input("Visit https://www.census.gov/programs-surveys/community-resilience-estimates/data/supplement.html\n"+
                "and save the file with file name `cre_equity_census_tract_data.csv`\n"+
                "in the `raw_data` folder located above this folder.\n"+
                "Press `enter` when finished.")
            cre_equity = pd.read_csv(file_path_name, encoding='latin1')
    
    # get the last 11 characters of the GEO_ID which contains the census tract
    cre_equity['location_id'] = cre_equity['GEO_ID'].apply(lambda x: x[-11:]).astype(str)

    # define columns to keep
    cols_keep = ['location_id',
                'NAME',
                'NH_Black_alone_PE',
                'NH_White_alone_PE',
                'Hispanic_PE',
                'PRED3_PE',
                'Blw_Pov_Lvl_PE',
                'No_Health_Ins_PE',
                'Male_PE',
                'Female_PE',
                'GINI_IND_Inequality_E',
                'HS_Grad_PE',
                'No_Veh_PE',
                'Broadband_PE']

    cre_equity = cre_equity[cols_keep].copy(deep=True)
    # returned cleaned dataframe
    return(cre_equity)

def join_and_clean():
    """
    Call other functions to generate dataframes, join them, clean column names, and write file
    """
    # grab all data 
    depress_df = depression_data()
    walkability_df = walkability_data()
    cre_data = cre_equity_data()

    # join all data using depression data as the base since it already has a location filter
    joined_file = depress_df.merge(cre_data, left_on = 'LocationID', right_on = 'location_id', how = 'inner')
    joined_file = joined_file.merge(walkability_df, left_on='LocationID', right_on='location_id', how = 'left')

    # clean column names
    rename_cols = {'LocationID': 'census_tract_id',
                    'NAME': 'census_tract_name',
                    'Data_Value': 'depressed_perc',
                    'NH_Black_alone_PE':'black_non_hisp_perc',
                    'NH_White_alone_PE':'white_non_hisp_perc',
                    'Hispanic_PE':'hispanic_latino_perc',
                    'PRED3_PE':'3_plus_cre_risk_factors_perc',
                    'Blw_Pov_Lvl_PE':'below_poverty_level_perc',
                    'No_Health_Ins_PE':'no_health_insurance_perc',
                    'Male_PE':'male_perc',
                    'Female_PE':'female_perc',
                    'GINI_IND_Inequality_E':'income_inequality_gini_index',
                    'HS_Grad_PE':'hs_grad_perc',
                    'No_Veh_PE':'households_no_vehicle_perc',
                    'Broadband_PE':'households_w_internet_perc',
                    'Median_NatWalkInd':'walkability_score'
                }
    clean_joined_file = joined_file.rename(rename_cols, axis='columns')
    clean_joined_file = clean_joined_file[rename_cols.values()]

    # write file and provide instructions
    clean_joined_file.to_csv(os.path.join(data_folder, 'joined_depression_cre_walkability.csv'), index=False)
    print("\n\nNumber of census tracts in final file: ", len(clean_joined_file))
    input("Final file is now located in `raw_data/joined_depression_cre_walkability.csv`.\n"+
        "Add this file to this Google Drive folder:\n"+
        "https://drive.google.com/drive/folders/19RfOfSc8TWcXz4FyNEEg8ixJrkYcYJ0W\n"+
        "then press enter.")


if __name__ == "__main__":
    input("Please make sure the following files exist in the `raw_data` folder:\n"+
        "\t- cre_equity_census_tract_data.csv\n"+
        "\t- depression_census_tract_data.csv\n"+
        "\t- walkability_census_block_data.csv\n"+
        "Once you have confirmed this, press `enter`.")
    join_and_clean()
    print("\n\n~*~*~*~*~*~* DONE CREATING FILE ✅ :) ~*~*~*~*~*~*")







