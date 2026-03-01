import os
import csv
import json
import pandas as pd

def generate_web_data():
    analysis_dir = "analysis"
    github_links_file = "github_links.csv"
    
    # Map project names to github links
    # This is a bit tricky as the github_links.csv doesn't have project names
    # Let's see if we can infer them from the link
    github_links = {}
    if os.path.exists(github_links_file):
        with open(github_links_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                link = row["GitHub Link"].strip()
                if link.endswith("/"):
                    link = link[:-1]
                project_name = link.split("/")[-1]
                github_links[project_name.lower()] = link

    all_projects = []
    features_set = set()

    for file in os.listdir(analysis_dir):
        if file.endswith("_project_correlation_analysis.csv"):
            file_path = os.path.join(analysis_dir, file)
            df = pd.read_csv(file_path)
            
            for _, row in df.iterrows():
                project_name = row["Project"]
                # Clean project name if it's a path
                clean_name = os.path.basename(project_name)
                
                project_data = {
                    "name": clean_name,
                    "benchmark": file.replace("_project_correlation_analysis.csv", ""),
                    "avg_cc": row.get("Avg CC", 0),
                    "avg_features_per_unit": row.get("Avg No. Features per unit", 0),
                    "no_units": row.get("No. Units", 0),
                    "total_features": row.get("Total Features", 0),
                    "github_link": github_links.get(clean_name.lower(), ""),
                    "features": {}
                }
                
                # Skip projects with NaN values in core metrics
                if pd.isna(project_data["avg_cc"]) or pd.isna(project_data["avg_features_per_unit"]):
                    continue
                
                # Extract JS: features
                for col in df.columns:
                    if col.startswith("JS:"):
                        val = row[col]
                        # Convert to boolean/int (1 or 0)
                        try:
                            is_present = float(val) > 0
                        except:
                            is_present = False
                        project_data["features"][col] = 1 if is_present else 0
                        features_set.add(col)
                
                all_projects.append(project_data)

    output = {
        "features": sorted(list(features_set)),
        "projects": all_projects
    }

    with open("web_data.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"Generated web_data.json with {len(all_projects)} projects.")

if __name__ == "__main__":
    generate_web_data()
