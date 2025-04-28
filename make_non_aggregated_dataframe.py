#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 25 11:43:01 2025

@author: miralombaert
"""

import pandas
import glob
import os

#%% Gather all file names in a list to be able to iterate over the file names

# Path to the folder containing all subject CSV files
RAW_folder_path = "/Users/miralombaert/Desktop/RPEP/Psychopy_script/RPEPdatafiles/"  # Adjust to your folder

# Combine all CSV file names into a list of datafile names
all_RAW_file_paths = glob.glob(RAW_folder_path + "*.csv")  # Finds all .csv files
print(f"The first file path: {all_RAW_file_paths[0]}")
print()
print(f"There are {len(all_RAW_file_paths)} subject files") #to check if all data files were found


#%% filter the data and calculate median: only keep the test data (not the practice data) where accuracy = 1 
#and only trials where the solution was actually present in the decision screen

N_trials, N_unusable_trials, N_unconscious_trials = 0, 0, 0 #keep track of the number of trials and the trials that are removed

for subject_number, RAW_file_path in enumerate(all_RAW_file_paths): #itterate over every file, and put all the trials together in one dataframe
    current_file = pandas.read_csv(RAW_file_path)
    
    
    #first calculate the accuracy score per subject
    percentage_accurate = len (current_file[(current_file['Accuracy'] == 1) & (current_file['Phase of Exp'] == 1)]) / len (current_file['Phase of Exp'] == 1)
    
    #only include trials that are correct, and that don't have an earlier lsatency than 180ms
    current_file_filtered = current_file[(current_file['Accuracy'] == 1) &
                                         (current_file['Phase of Exp'] == 1) &
                                         (current_file['correctresponse'] != 'space') &
                                         current_file['RT'] > 0.180]    
    
    N_trials += (current_file['Phase of Exp'] == 1).sum()
    N_unusable_trials += (current_file['Phase of Exp'] == 1).sum() - (current_file_filtered['Phase of Exp'] == 1).sum()
    
    #check how many trials have both shorter RT than 180 ms and are accurate at the same time
    N_unconscious_trials += ((current_file['RT'] < 0.180) & (current_file['Accuracy'] == 1) & (current_file['Phase of Exp'] == 1)).sum()
    
    selected_columns = ['interval', 'distractor_size', 'correctresponse_location', 'RT', 'solution', 'product', 'distractor', 'Block', 'Age', 'Gender', 'Handedness']
    RT_data = current_file_filtered[selected_columns].copy()
    
    # Replace 0 with 'left' and 1 with 'right' in 'correctresponse_location'
    RT_data['correctresponse_location'].replace({0: 'left', 1: 'right'}, inplace=True)
    RT_data['distractor_size'].replace({0: 'smaller', 1: 'bigger'}, inplace=True)

    RT_data['accuracy_rate'] = percentage_accurate #for every participant add a column with the rate of accurate trials
    RT_data['subject'] = subject_number + 1 # Add subject number column
    
    
    # Save to a CSV file in the map: 'preprocessed_data'
    file_name = os.path.basename(RAW_file_path)
    RT_data.to_csv(f'/Users/miralombaert/Desktop/RPEP/RPEPprocessed_datafiles/Preprocessed_Data/non_aggregated/RT_{file_name}', index = False)
    
print(N_trials)
print(N_unusable_trials)
print(N_unconscious_trials)
print(N_unusable_trials/N_trials)
#%% take out all the files that are preprocessed and merge them in one big dataframe


preprocessed_folder_path = "/Users/miralombaert/Desktop/RPEP/RPEPprocessed_datafiles/Preprocessed_Data/non_aggregated/"  # Adjust to your folder

# Combine all CSV files into one dataframe 
all_preprocessed_file_paths = glob.glob(preprocessed_folder_path + "*.csv")  # Finds all .csv files
print(f"The first file path: {all_preprocessed_file_paths[0]}") 
print()
print(f"There are {len(all_preprocessed_file_paths)} preprocessed subject files") #to check if all subjects are included


# Initialize an empty list to hold dataframes
dataframes = []

for preprocessed_file_path in all_preprocessed_file_paths: #discard the participant that has too low an accuracy
    current_file = pandas.read_csv(preprocessed_file_path)  # Read each preprocessed file
    dataframes.append(current_file)  # Add it to the list


# Concatenate all dataframes into one
combined_dataframe = pandas.concat(dataframes, ignore_index=True)

# Save the combined dataframe to a CSV
combined_csv_path = "/Users/miralombaert/Desktop/RPEP/RPEPprocessed_datafiles/final_dataframe/RPEP_dataframe_non_aggregated.csv"
combined_dataframe.to_csv(combined_csv_path, index=False)

print(f"Combined data saved at: {combined_csv_path}")







