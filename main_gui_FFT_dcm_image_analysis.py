import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import json
import threading

# Path to the configuration file
CONFIG_FILE = "last_inputs.json"

def load_last_inputs():
    """Load the last used inputs from a JSON file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                return json.load(file)
        except Exception:
            return {}
    return {}

def save_last_inputs(inputs):
    """Save the current inputs to a JSON file."""
    try:
        with open(CONFIG_FILE, "w") as file:
            json.dump(inputs, file)
    except Exception as e:
        print(f"Error saving inputs: {e}")

def run_analysis():
    # Get user inputs
    input_folder = folder_path.get()
    output_folder = output_path.get()  # Get the output folder
    sagittal_slice_idx = slice_idx_entry.get()
    periodicity = periodicity_entry.get()
    std_factor = std_factor_entry.get()  # Get the std factor input value

    # Validate inputs
    if not input_folder or not os.path.isdir(input_folder):
        messagebox.showerror("Error", "Invalid input folder.")
        return
    if not output_folder or not os.path.isdir(output_folder):  # Validate output folder
        messagebox.showerror("Error", "Invalid output folder.")
        return
    try:
        sagittal_slice_idx = int(sagittal_slice_idx)
        periodicity = int(periodicity)
        std_factor = float(std_factor)  # Convert std_factor to float
    except ValueError:
        messagebox.showerror("Error", "Slice index, periodicity, and std factor must be valid numbers.")
        return

    # Save the current inputs
    save_last_inputs({
        "input_folder": input_folder,
        "output_folder": output_folder,  # Save output folder to config
        "sagittal_slice_idx": sagittal_slice_idx,
        "periodicity": periodicity,
        "std_factor": std_factor,  # Save std factor to config
    })

    # List all files in the input folder
    files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

    # Sort the files in ascending order
    files.sort()
    
    # make a shortened version to pass on via a jscon
    files_num_short = [f"{i+1}_{files.split('.')[0]}" for i, files in enumerate(files)]
    

    # Update progress bar
    progress_bar["maximum"] = len(files)
    progress_bar["value"] = 0

    # Variables to accumulate results
    accumulated_results = []  # Full results (stdout + errors)
    filename_list = [] 
    stdout_results = []       # Only stdout content

    # Function to process a single file
    def process_file(filename):
        nonlocal accumulated_results, stdout_results  # Access outer variables
        filepath = os.path.join(input_folder, filename)
        try:
            result = subprocess.run(
                [
                    "python",
                    "FFT_dcm_image_analysis.py",
                    filepath,
                    str(sagittal_slice_idx),
                    str(periodicity),
                ],
                capture_output=True,
                text=True,
            )

            # Accumulate the full result
            if result.returncode == 0:
                stdout = result.stdout.strip()
                accumulated_results.append(f"{filename}: {stdout}")
                filename_list.append(f"{filename}")
                stdout_results.append(stdout)  # Accumulate only the stdout content
            else:
                stderr = result.stderr.strip()
                accumulated_results.append(f"{filename}: Error - {stderr}")

        except Exception as e:
            accumulated_results.append(f"{filename}: Error - {str(e)}")

        # Update progress bar
        progress_bar["value"] += 1
        root.update_idletasks()

    # Function to process files sequentially
    def process_files_sequentially():
        try:
            # Process each file in sequence
            for filename in files:
                process_file(filename)

            # After processing, write all accumulated results to the output folder as 'match_score.txt'
            output_file_path = os.path.join(output_folder, "match_score.txt")  # Add 'match_score.txt'
            with open(output_file_path, "w") as out_file:
                out_file.write("\n".join(accumulated_results))

            # Convert accumulated_results and stdout_results to JSON strings
            accumulated_results_json = json.dumps(accumulated_results)
            filename_list_json = json.dumps(files_num_short)         
            stdout_results_json = json.dumps(stdout_results)

            # Call the other script and pass stdout_results and std_factor as arguments
            try:
                result = subprocess.run(
                    [
                        "python",
                        "find_and_plot_outlier.py",  # Replace with the name of your script
                        input_folder,
                        filename_list_json,
                        stdout_results_json,
                        str(std_factor),  # Pass std_factor to other_script.py
                        output_folder
                    ],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print("------------- input ----------------")
                    print(result.stdout)
                else:
                    print("Other script error:", result.stderr)
            except Exception as e:
                print(f"Error running other script: {e}")

            messagebox.showinfo("Success", f"Analysis completed. Results saved to {output_file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process files: {str(e)}")



    # Run the processing in a separate thread to avoid freezing the GUI
    threading.Thread(target=process_files_sequentially, daemon=True).start()


# Load the last inputs
last_inputs = load_last_inputs()

# Create the GUI
root = tk.Tk()
root.title("Batch Match Score Analyzer")

# Input folder
tk.Label(root, text="Input Folder:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
folder_path = tk.StringVar(value=last_inputs.get("input_folder", ""))
tk.Entry(root, textvariable=folder_path, width=50).grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: folder_path.set(filedialog.askdirectory())).grid(row=0, column=2, padx=10, pady=5)

# Output folder
tk.Label(root, text="Output Folder:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
output_path = tk.StringVar(value=last_inputs.get("output_folder", ""))
tk.Entry(root, textvariable=output_path, width=50).grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: output_path.set(filedialog.askdirectory())).grid(row=1, column=2, padx=10, pady=5)

# Sagittal slice index
tk.Label(root, text="Sagittal Slice Index:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
slice_idx_entry = tk.Entry(root, width=10)
slice_idx_entry.grid(row=2, column=1, sticky="w", padx=10, pady=5)
slice_idx_entry.insert(0, last_inputs.get("sagittal_slice_idx", "0"))  # Default value

# Periodicity
tk.Label(root, text="Periodicity:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
periodicity_entry = tk.Entry(root, width=10)
periodicity_entry.grid(row=3, column=1, sticky="w", padx=10, pady=5)
periodicity_entry.insert(0, last_inputs.get("periodicity", "1"))  # Default value

# Std factor
tk.Label(root, text="Std Factor:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
std_factor_entry = tk.Entry(root, width=10)
std_factor_entry.grid(row=4, column=1, sticky="w", padx=10, pady=5)
std_factor_entry.insert(0, last_inputs.get("std_factor", "3.0"))  # Default value

# Progress Bar
tk.Label(root, text="Progress:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
progress_bar = ttk.Progressbar(root, length=300, mode="determinate")
progress_bar.grid(row=5, column=1, columnspan=2, pady=10)

# Run button
tk.Button(root, text="Run", command=run_analysis, width=20).grid(row=6, column=1, pady=10)

root.mainloop()
