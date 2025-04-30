import pandas as pd
import json
from collections import defaultdict

# TODO keyra fyrir öll project í benchmark, hvaða benchmark?
# TODO average coverage segir ekki mikið eitt og sér, get ég fundið coverage prósentuna? eða miðað við branches/statements á unitinu sjálfu,
# TODO Skila niðurstöðum, average failrate fyrir units með X feature per project og per benchmark, líka f coverage
# TODO Skiptir þá ekki máli að projectin séu partur af feature benchmark því við sjáum hvort þetta feature sé í því eða ekki...
# TODO what to do about that there are more than one test generated per unit under test?? Anything? maybe not
# TODO cant map units perfectly between require units and my unit finding per file

# Load CSV
csv_path = "results/eslint_results_test_dropzone.csv"
df_units = pd.read_csv(csv_path)

# Load JSON
json_path = "../testpilot/output_all/output_custom/output_dropzone/report.json"
with open(json_path, 'r') as f:
    test_report = json.load(f)

# Prepare data structures
feature_stats = defaultdict(lambda: {'failures': 0, 'passes': 0, 'coverage_counts': []})

# Iterate over tests
for test in test_report['tests']:
    targeted_api = test.get('api').split('.')[-1]
    status = test.get('status')
    coverage = len(test.get('coveredStatements', []))

    # Match with units in CSV - If units have the same name, skip - todo fix later to match better api to file
    matched_units = df_units[df_units['Unit'] == targeted_api]
    print(matched_units)
    if len(matched_units)>1:
        continue
    for _, unit in matched_units.iterrows():
        for feature in unit.index:
            if 'JS:' in feature and unit[feature] == 1:  # Assuming binary feature flags
                if status == 'FAILED':
                    feature_stats[feature]['failures'] += 1
                elif status == 'PASSED':
                    feature_stats[feature]['passes'] += 1
                feature_stats[feature]['coverage_counts'].append(coverage)

# Compute fail rate and average coverage per feature
results = []
for feature, stats in feature_stats.items():
    total_tests = stats['failures'] + stats['passes']
    fail_rate = stats['failures'] / total_tests if total_tests > 0 else 0
    avg_coverage = sum(stats['coverage_counts']) / len(stats['coverage_counts']) if stats['coverage_counts'] else 0
    results.append({
        'feature': feature,
        'fail_rate': fail_rate,
        'average_coverage': avg_coverage
    })

# Convert to DataFrame for easy viewing
results_df = pd.DataFrame(results)
print(results_df)

# Optional: Save to CSV
results_df.to_csv('feature-analysis/feature_analysis_results_dropzone.js.csv', index=False)
