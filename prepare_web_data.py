import os
import csv
import json
import pandas as pd
import re

def generate_web_data():
    analysis_dir = "analysis_results"
    github_links_file = "github_links.csv"

    repo_links = {}
    
    # 1. Load from github_links.csv
    if os.path.exists(github_links_file):
        with open(github_links_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                link = row["GitHub Link"].strip()
                if link.endswith("/"):
                    link = link[:-1]
                project_name = link.split("/")[-1]
                repo_links[project_name.lower()] = link

    benchmark_files = {
        "JavaScriptRepos": "JavaScriptRepos.txt",
        "TypeScriptRepos": "TypeScriptRepos.txt",
        "VueRepos": "VueRepos.txt"
    }

    for folder, filename in benchmark_files.items():
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    for repo in data.get("repositories", []):
                        repo_full_name = repo.get("repoFullName")
                        if repo_full_name:
                            project_name = repo_full_name.split("/")[-1]
                            link = f"https://github.com/{repo_full_name}"
                            repo_links[project_name.lower()] = link
                except json.JSONDecodeError:
                    print(f"Error decoding {file_path}")

    # 3. Load from TestPilot-Benchmark/clone.sh
    testpilot_clone_sh = os.path.join("TestPilot-Benchmark", "clone.sh")
    if os.path.exists(testpilot_clone_sh):
        with open(testpilot_clone_sh, "r", encoding="utf-8") as f:
            content = f.read()
            # Simple regex to find URLs in the shell script
            links = re.findall(r'https?://[^\s"]+', content)
            for link in links:
                clean_link = link.strip().strip('"').strip("'")
                if clean_link.endswith(".git"):
                    clean_link = clean_link[:-4]
                project_name = clean_link.split("/")[-1]
                repo_links[project_name.lower()] = clean_link

    seen_projects = {}
    features_set = set()

    for file in os.listdir(analysis_dir):
        if file.endswith("_project_analysis_results.csv"):
            file_path = os.path.join(analysis_dir, file)
            df = pd.read_csv(file_path)
            
            for _, row in df.iterrows():
                project_name = row["Project"]
                # Clean project name if it's a path
                clean_name = os.path.basename(str(project_name))
                
                benchmark_name = row.get("Benchmark", file.replace("_project_analysis_results.csv", ""))
                # Remove "-Benchmark" or " Benchmark" part
                benchmark_name = benchmark_name.replace("-Benchmark", "").replace(" Benchmark", "").replace("_Benchmark", "")
                
                repo_link = repo_links.get(clean_name.lower(), "")
                
                project_data = {
                    "name": clean_name,
                    "benchmark": benchmark_name,
                    "avg_cc": row.get("Avg CC", 0),
                    "avg_features_per_unit": row.get("Avg No. Features per unit", 0),
                    "no_units": row.get("No. Units", 0),
                    "features_covered": row.get("Features Covered", 0),
                    "repo_link": repo_link,
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
                
                # Check for duplicates based on name
                if clean_name not in seen_projects:
                    seen_projects[clean_name] = project_data
                else:
                    # If duplicate, prioritize the one with repo_link
                    if not seen_projects[clean_name]["repo_link"] and project_data["repo_link"]:
                        seen_projects[clean_name] = project_data

    all_projects = list(seen_projects.values())
    output = {
        "features": sorted(list(features_set)),
        "projects": all_projects
    }

    with open("web_data.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"Generated web_data.json with {len(all_projects)} projects.")

if __name__ == "__main__":
    generate_web_data()
