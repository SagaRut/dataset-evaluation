import os
from pathlib import Path
import pandas as pd
from collections import defaultdict

evaluation_results_directory = "evaluation_results/"
output_directory = "analysis_results/"

FILTER_CC = 2
FILTER_AVG_FEATURES = 3

def analyze_results(directory):
    benchmarks = defaultdict(lambda: {"project": [], "file": [], "unit": []})
    all_projects = []

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)

        if file.startswith("eslint_results") and file.endswith(".csv"):
            project = file.split("_")[3].replace(".csv", "")
            benchmark = file.split("_")[2]
            eslint_results = pd.read_csv(file_path)
            js_features = [col for col in eslint_results.columns if col.startswith("JS:")]
            
            # Unit-level results
            for _, row in eslint_results.iterrows():
                unit_row = {
                    "Benchmark": benchmark,
                    "Project": project,
                    "File": row["File"],
                    "Unit": row["Unit"],
                    "LOC": row["LOC"],
                    "CC": row["CC"]
                }
                for feat in js_features:
                    unit_row[feat] = row[feat]
                benchmarks[benchmark]["unit"].append(unit_row)

            # File-level results
            grouped_by_file = eslint_results.groupby("File")
            for file_name, group in grouped_by_file:
                used_features_file = group[js_features].sum(axis=0)
                no_features_covered_file = (used_features_file > 0).sum()
                ratio_feature_coverage_file = no_features_covered_file / len(js_features) if js_features else 0
                
                file_row = {
                    "Benchmark": benchmark,
                    "Project": project,
                    "File": file_name,
                    "No. Units": len(group),
                    "Avg CC": group["CC"].mean(),
                    "Avg No. Features per unit": group[js_features].sum(axis=1).mean() if js_features else 0,
                    "Features Covered": ratio_feature_coverage_file,
                }
                for feat in js_features:
                    file_row[feat] = used_features_file[feat]
                benchmarks[benchmark]["file"].append(file_row)

            # Project-level results
            used_features = eslint_results[js_features].sum(axis=0)
            no_features_covered = (used_features > 0).sum()
            total_features = len(js_features)
            ratio_feature_coverage = no_features_covered / total_features if total_features else 0
            complexity = float(eslint_results["CC"].mean())
            avg_no_features = float(eslint_results[js_features].sum(axis=1).mean()) if js_features else None

            project_results = {
                "Benchmark": benchmark,
                "Project": project,
                "No. Units": len(eslint_results),
                "Avg CC": complexity,
                "Avg No. Features per unit": avg_no_features,
                "Features Covered": ratio_feature_coverage,
            }

            for feat in js_features:
                project_results[feat] = used_features[feat]

            benchmarks[benchmark]["project"].append(project_results)
            all_projects.append(project_results)

    return benchmarks, all_projects


benchmarks, all_projects = analyze_results(evaluation_results_directory)

# Ensure output directory exists
os.makedirs(output_directory, exist_ok=True)

# Save per-benchmark analysis CSVs
for benchmark, results in benchmarks.items():
    if results["project"]:
        pd.DataFrame(results["project"]).to_csv(
            Path(output_directory) / f"{benchmark}_project_analysis_results.csv",
            index=False
        )
    if results["file"]:
        pd.DataFrame(results["file"]).to_csv(
            Path(output_directory) / f"{benchmark}_file_analysis_results.csv",
            index=False
        )
    if results["unit"]:
        pd.DataFrame(results["unit"]).to_csv(
            Path(output_directory) / f"{benchmark}_unit_analysis_results.csv",
            index=False
        )

# Filter projects and save filtered results
if all_projects:
    all_projects_df = pd.DataFrame(all_projects)
    js_features = [col for col in all_projects_df.columns if col.startswith("JS:")]
    
    filtered_df = all_projects_df[
        (all_projects_df["Avg CC"] >= FILTER_CC) & 
        (all_projects_df["Avg No. Features per unit"] >= FILTER_AVG_FEATURES)
    ].copy()

    if not filtered_df.empty:
        # Check if all features are present in the whole set of filtered projects
        all_features_present = filtered_df[js_features].sum(axis=0) > 0
        filtered_df["All Features Present in whole list"] = all_features_present.all()
        
        filtered_df.to_csv(
            Path(output_directory) / "filtered_projects_with_analysis_result.csv",
            index=False
        )

print("Results saved per benchmark and filtered results saved.")
