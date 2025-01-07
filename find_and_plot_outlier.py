import sys
import json
import os
import argparse
import matplotlib.pyplot as plt
import numpy as np
import ast

# find match score outliers 
def find_outliers(input, std_factor):

    #print("scores:", input)
    
    # Convert the list of string values to a list of floats
    scores = [float(score) for score in input]
    
    #print("scores:", scores)
    
    
    std_factor = float(std_factor)
    mean_value = np.mean(scores)
    std_value = np.std(scores)
    


        
    # Identify outliers as those beyond the threshold of mean ± (std_factor * std_value)
    outliers_indices = [
        i for i, score in enumerate(scores) if abs(score - mean_value) > std_factor * std_value
    ]



      
    return outliers_indices




def plot_match_scores(input, output_path, std_factor, outlier_indices):

    
    #print(f"Mean of match scores: {mean_value}")

    

    # Convert the list of string values to a list of floats
    scores = [float(score) for score in input]
    #print("scores_for_plot:", scores)

    std_factor = float(std_factor)
    mean_value = np.mean(scores)
    std_value = np.std(scores)
    threshold = std_factor * std_value

    deviation_vector = [score - mean_value for score in scores]



    # Generate x-axis values (assuming sequential order)
    x = list(range(1, len(deviation_vector) + 1))

    # Plot the data
    deviation_vector_abs = np.abs(deviation_vector)
    plt.figure(figsize=(16, 6))  # Double the width (16) compared to the original (8)
    plt.plot(x, deviation_vector_abs, linestyle='-', color='b', label='Match Score')  # Plot match scores

    # Highlight the outliers
    plt.scatter(
        [x[i] for i in outlier_indices],
        [deviation_vector_abs[i] for i in outlier_indices],
        color='red',
        label=f'Outliers (> {std_factor} stds)',
        zorder=5
    )
    
    # Add a horizontal line for the threshold
    plt.axhline(y=threshold, color='r', linestyle='--', label="threshold")
    
    
    # Title and labels
    # plt.title('Match Scores with Outliers')
    outlier_indices_p1 = [i + 1 for i in outlier_indices]
    plt.title(f'Match Scores with Outliers: {outlier_indices_p1}')
    plt.xlabel('Index')
    plt.ylabel('Match Score')
    plt.grid(True)
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(os.path.join(output_path, "match_score_plot.png"))
    print(f"Plot saved to {output_path}")

    # Optionally, show the plot
    plt.show()



if __name__ == "__main__":
    # Get the JSON argument
    input_folder = sys.argv[1]
    filename_list = sys.argv[2]
    filename_list = ast.literal_eval(filename_list)
    accumulated_results_json = sys.argv[3]    
    std_factor = sys.argv[4]
    output_folder = sys.argv[5] 

    # printing
    print("input_folder:", input_folder)
    print("filename_list:", filename_list)
    accumulated_results = json.loads(accumulated_results_json)
    print("Received accumulated_results:", accumulated_results)    
    print("std_factor:", std_factor)
    print("output_folder:", output_folder)
    
    
    # Identify outliers based on standard deviation threshold
    #outlier_indices, mean_value, std_value = find_outliers(accumulated_results, std_factor)
    outliers_indices = find_outliers(accumulated_results, std_factor)


    #outlier_names = [filename_list[i] for i in outliers_indices]
    outlier_filenames = [filename_list[i] for i in outliers_indices]

    print("------------- output ----------------")
    print("outliers_indices:", outliers_indices)
    print("Outlier Names:", outlier_filenames)
 
 
    plot_match_scores(accumulated_results,output_folder,std_factor,outliers_indices)
