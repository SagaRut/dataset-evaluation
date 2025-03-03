import csv
import os
import pandas as pd
from scipy.stats import entropy
from itertools import combinations
from collections import defaultdict
from collections import Counter

# FEATURE_LOOKUP = "JS:PropertyAccess"
# FEATURE_LOOKUP = "JS:Closures"
FEATURE_LOOKUP = "JS:Async"
# FEATURE_LOOKUP = "JS:Prototype"
PROJECT_LIST = []

def analyze_benchmark(directory):
    all_benchmark_results = []  # To store results for all benchmarks (1 line per benchmark)
    all_project_results = []  # To store results for all projects (1 line per project)
    benchmarks = defaultdict(lambda: {"dataset": {}, "project": []})  # To store dataset and project results

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)

        # Processing the dataset (average_results) files
        if file.startswith("average_results") and file.endswith(".csv"):
            benchmark = file.replace("average_results_", "").replace(".csv", "")
            average_results = pd.read_csv(file_path)
            js_features = [col for col in average_results.columns if col.startswith("JS:")]
            total_features = len(js_features)

            if total_features > 0:
                features_covered = average_results[js_features].any().sum()
                completeness = features_covered / total_features
            else:
                completeness = 0

            dataset_summary = average_results.describe()

            dataset_results = {
                "Benchmark": benchmark,
                "Completeness": completeness,
                "Avg LOC": dataset_summary.loc["mean", "Average LOC"] if "Average LOC" in dataset_summary else None,
                "Avg CC": dataset_summary.loc["mean", "Average CC"] if "Average CC" in dataset_summary else None,
                "Total Units": dataset_summary.loc["count", "Average CC"]*dataset_summary.loc["mean", "Number of units"] if "Number of units" in dataset_summary else None,
                "Avg number of Units": dataset_summary.loc["mean", "Number of units"] if "Number of units" in dataset_summary else None,
                "Avg JS Features": dataset_summary.loc[
                    "mean", "Average Number of JS Features"] if "Average Number of JS Features" in dataset_summary else None
            }
            benchmarks[benchmark]["dataset"] = dataset_results  # Store dataset results for each benchmark

            # Append dataset results to all_benchmark_results (one line per benchmark)
            all_benchmark_results.append(dataset_results)

        # Processing the project (eslint_results) files
        elif file.startswith("eslint_results") and file.endswith(".csv"):
            project = file.split("_")[3].replace(".csv", "")
            benchmark = file.split("_")[2]  # Extract benchmark from the file
            eslint_results = pd.read_csv(file_path)
            js_features = [col for col in eslint_results.columns if col.startswith("JS:")]
            used_features = eslint_results[js_features].sum(axis=0)
            no_features_covered = (used_features > 0).sum()
            total_features = len(js_features)
            ratio_feature_coverage = no_features_covered/total_features
            list_features_covered = used_features[used_features > 0].index.tolist()
            if js_features and eslint_results[js_features].sum(axis=0).sum() > 0:
                feature_proportions = eslint_results[js_features].sum(axis=0) / eslint_results[js_features].sum(
                    axis=0).sum()
                feature_entropy = entropy(feature_proportions)
            else:
                feature_entropy = 0

            pairwise_interactions = {}
            for f1, f2 in combinations(js_features, 2):
                pairwise_interactions[(f1, f2)] = int(
                    (eslint_results[f1] & eslint_results[f2]).sum())  # Convert sum to int

            # Extract top 5 pairwise interactions
            top_interactions = dict(sorted(pairwise_interactions.items(), key=lambda x: x[1], reverse=True)[:5])

            # Convert tuple keys to a safer string format for CSV (e.g., 'JS:DynamicTyping_JS:NestedFunction')
            # We will now join keys with an underscore and remove the curly braces
            top_interactions_str = "; ".join([f"{k[0]}_{k[1]}: {v}" for k, v in top_interactions.items()])

            complexity = float(eslint_results["CC"].mean())

            avg_no_features = float(eslint_results[js_features].sum(axis=1).mean()) if js_features else None
            project_results = {
                "Benchmark": benchmark,  # Store benchmark name
                "Project": project,  # Store project name
                "Features Covered": ratio_feature_coverage,  # Percentage of features covered
                "Total JS Features Per Unit (Mean)": avg_no_features,  # Cast to float to avoid np.int64
                "Avg Complexity": complexity,
                "Feature Entropy": feature_entropy,
                "Top Pairwise Interactions": top_interactions_str,  # Use custom string format
                "Features covered": list_features_covered,
            }

            if FEATURE_LOOKUP in list_features_covered:
                if complexity>=2:
                    PROJECT_LIST.append([benchmark, project, avg_no_features, complexity])

            # Append project results to the benchmark's project list
            benchmarks[benchmark]["project"].append(project_results)

            # Append project results to all_project_results (one line per project)
            all_project_results.append(project_results)

    return benchmarks, all_benchmark_results, all_project_results


# Directory containing the benchmark files (results of evaluating each unit of each project)
benchmark_directory = "results/"

# Run the analysis
benchmarks, benchmark_results, project_results = analyze_benchmark(benchmark_directory)

no_total_features = 9
for benchmark, results in benchmarks.items():
    features_covered = []
    for project in results["project"]:
        features_covered.extend(project["Features covered"])
    count = Counter(features_covered)
    features_covered = set(features_covered)
    for benchmark_in_results in benchmark_results:
        if benchmark_in_results["Benchmark"] == benchmark:
            benchmark_in_results["Number of Projects"] = len(results["project"])
            benchmark_in_results["Features Covered"] = len(features_covered)/no_total_features
            benchmark_in_results["Features Count"] = count

# Save per benchmark and aggregated results
os.makedirs("analysis", exist_ok=True)

# Save the aggregated benchmark results (one line per benchmark)
aggregated_benchmark_file = "analysis/all_benchmarks_analysis_results.csv"
pd.DataFrame(benchmark_results).to_csv(aggregated_benchmark_file, index=False)

# Save individual project results for each benchmark (one line per project)
for benchmark, results in benchmarks.items():
    if results["project"]:  # Only save if there are project results
        project_file = f"analysis/{benchmark}_project_analysis_results.csv"
        pd.DataFrame(results["project"]).to_csv(project_file, index=False)

directory = "analysis"
file_path = os.path.join(directory, f"feature_projects_{FEATURE_LOOKUP.split(':')[1]}.csv")

with open(file_path, mode="w", newline="") as file:
    writer = csv.writer(file)
    for item in PROJECT_LIST:
        writer.writerow([item])

print(f"Results saved per benchmark and aggregated across all benchmarks.")
print(f"Aggregated benchmark results saved to {aggregated_benchmark_file}")
