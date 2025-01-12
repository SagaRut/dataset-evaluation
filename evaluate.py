import os
import subprocess
import json
import csv
import re

# Path to the ESLint config file
ESLINT_CONFIG = "eslint.config.js"

# Only evaluate units that are exported
# Todo how to evaluate cyclomatic complexity of units that are exported classes?
# Todo How does the llm eval plugin find units, also classes??
# Todo setup JS feature
# TODO rest of JS features, finna instance, fyrst og gera evaluation á complexity miðað við það/coverage af hlutum?
# TODO rest af hlutum sem Mitchell talaði um
# Todo Skoða TestPilot/CoPilot og SynTest setup
# Todo Gera lista af benchmarks sem ég ætla að evaluate-a
# Todo Fá niðurstöður úr eh benchmarks
# Todo function, class, method, hvað er eigilega unit? finna cc fyrir allt?
# TODO set up eslint properly w package.json

# TODO add a part where it clones the repos by itself, have a list of files to include???
def install_eslint_and_plugins():
    """Ensure ESLint and required plugins are installed."""
    try:
        print("Checking and installing ESLint and plugins...")
        subprocess.run(["npm", "install", "-g", "eslint"], check=True, shell=True)
        print("Installing complexity plugin.")
        subprocess.run(["npm", "install", "eslint-plugin-complexity", "--save-dev"], check=True, shell=True)
        print("ESLint and plugins installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing ESLint or plugins: {e}")
        exit(1)

def run_eslint_on_files(files):
    """Run ESLint on a list of files and return the results."""
    results = []
    for file in files:
        try:
            print(f"Running ESLint on {file}")
            result = subprocess.run(
                ["npx", "eslint", file, "--config", ESLINT_CONFIG, "--format", "json"],
                capture_output=True,
                text=True,
                shell=True
            )
            if result.stdout:
                eslint_results = json.loads(result.stdout)
                for eslint_result in eslint_results:
                    # Extract filePath and split into project and file name
                    file_path = eslint_result["filePath"]
                    path, file_name = os.path.split(file_path)
                    path, project_name = os.path.split(path)

                    # Add the project path and file name to the result
                    eslint_result["project"] = project_name
                    eslint_result["fileName"] = file_name
                    eslint_result["exportedUnits"] = []
                    eslint_result["LOC"] = {}
                    eslint_result["CC"] = {}
                    eslint_result["JS:Async"] = {}
                    eslint_result["JS:DynamicTyping"] = {}
                    eslint_result["JS:DomInteraction"] = {}
                    eslint_result["JS:NestedFunction"] = {}
                    eslint_result["JS:HigherOrder"] = {}

                    # Find exported units
                    for message in eslint_result["messages"]:
                        # Find exported units
                        if message["ruleId"] == "find-units/find-units":
                            unit = re.search(r"found:\s+([a-zA-Z_$][\w$]*)", message["message"])
                            if unit:
                                # Append the matched unit to the list
                                eslint_result["exportedUnits"].append(unit.group(1))
                        if message["ruleId"] == "LOC/LOC":
                            unit = re.search(r"Unit\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            loc = re.search(r"has (\d+)", message["message"])
                            if unit and loc:
                                # Add the unit name as the key and LOC value as the value
                                eslint_result["LOC"][unit.group(1)] = int(loc.group(1))
                        if message["ruleId"] == "complexity":
                            unit = re.search(r"Function\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            cc = re.search(r"complexity of (\d+)", message["message"])
                            if unit and cc:
                                # Add the unit name as the key and CC value as the value
                                eslint_result["CC"][unit.group(1)] = int(cc.group(1))
                        if message["ruleId"] == "contains-async/find-async":
                            unit = re.search(r"function\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:Async"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-dynamic-typing/find-dynamic-typing":
                            unit = re.search(r"function\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:DynamicTyping"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-dom/find-dom-interaction":
                            unit = re.search(r"function\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:DomInteraction"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-nested-function/find-nested-function":
                            unit = re.search(r"function\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:NestedFunction"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-higher-order/find-higher-order":
                            unit = re.search(r"function\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:HigherOrder"][unit.group(1)] = 1
                    # Add the updated result to results list
                    results.append(eslint_result)
            else:
                print(f"No output for {file}. Exit code: {result.returncode}")
        except Exception as e:
            print(f"Unexpected error running ESLint on {file}: {e}")
    return results

def reformat_data(results):
    json_data = []
    for result in results:
        for unit in result["exportedUnits"]:
            loc = result["LOC"].get(unit, 0)  # Default LOC to 0 if not found
            cc = result["CC"].get(unit, 0)  # Default CC to 0 if not found
            asyncFound = result["JS:Async"].get(unit, 0)  # Default to 0 if not found
            dynamicTyping = result["JS:DynamicTyping"].get(unit, 0)  # Default to 0 if not found
            domInteraction = result["JS:DomInteraction"].get(unit, 0)  # Default to 0 if not found
            nestedFunction = result["JS:NestedFunction"].get(unit, 0)  # Default to 0 if not found
            higherOrder = result["JS:HigherOrder"].get(unit, 0)  # Default to 0 if not found
            # Add to JSON data
            json_data.append({
                "Project": result["project"],
                "File": result["fileName"],
                "Unit": unit,
                "LOC": loc,
                "CC": cc,
                "JS:Async": asyncFound,
                "JS:DynamicTyping": dynamicTyping,
                "JS:DomInteraction": domInteraction,
                "JS:NestedFunction": nestedFunction,
                "JS:HigherOrder": higherOrder
            })
    return json_data

def save_results_to_file(results, reformatted_results, json_file, csv_file):
    """Save ESLint results to JSON and CSV files."""
    with open(json_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Results saved to {json_file}")

    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Project", "File", "Unit", "LOC", "CC",
                         "JS:Async", "JS:DynamicTyping", "JS:DomInteraction",
                         "JS:NestedFunction", "JS:HigherOrder"])
        for result in reformatted_results:
            writer.writerow([
                result["Project"],
                result["File"],
                result["Unit"],
                result["LOC"],
                result["CC"],
                result["JS:Async"],
                result["JS:DynamicTyping"],
                result["JS:DomInteraction"],
                result["JS:NestedFunction"],
                result["JS:HigherOrder"],
            ])
    print(f"Results saved to {csv_file}")


def calculate_average_results(results):
    """Calculate average LOC and CC per project."""
    # TODO calculate average number/number of JS features found
    project_data = {}

    # Group results by project
    for result in results:
        project = result["Project"]
        loc = result["LOC"]
        cc = result["CC"]
        noOfJSFeatures = sum(value for key, value in result.items() if key.startswith('JS'))

        if project not in project_data:
            project_data[project] = {"LOC": [], "CC": [], "JSFeatures": []}

        project_data[project]["LOC"].append(loc)
        project_data[project]["CC"].append(cc)
        project_data[project]["JSFeatures"].append(noOfJSFeatures)

    # Calculate averages
    averages = []
    for project, metrics in project_data.items():
        avg_loc = sum(metrics["LOC"]) / len(metrics["LOC"])
        avg_cc = sum(metrics["CC"]) / len(metrics["CC"])
        avg_noJSFeatures = sum(metrics["JSFeatures"]) / len(metrics["JSFeatures"])
        averages.append({"Project": project, "Average LOC": avg_loc, "Average CC": avg_cc, "Average Number of JS Features": avg_noJSFeatures})

    return averages


def save_averages_to_file(averages, json_file, csv_file):
    """Save averages to JSON and CSV files."""
    # Save to JSON
    with open(json_file, "w") as jf:
        json.dump(averages, jf, indent=4)

    # Save to CSV
    with open(csv_file, "w", newline="") as cf:
        writer = csv.DictWriter(cf, fieldnames=["Project", "Average LOC", "Average CC", "Average Number of JS Features"])
        writer.writeheader()
        writer.writerows(averages)

def main():
    # Ensure npm packages are installed
    install_eslint_and_plugins()

    # Directory containing projects
    project_dir = "JS-projects"

    all_results = []

    # Iterate over projects in the directory
    for project in os.listdir(project_dir):
        project_path = os.path.join(project_dir, project)
        if os.path.isdir(project_path):
            print(f"Processing project: {project_path}")

            # Get all JavaScript files in the project
            files = [
                os.path.join(root, file)
                for root, _, filenames in os.walk(project_path)
                for file in filenames if file.endswith(".js")
            ]
            print(f"Found {len(files)} files in project: {project_path}")

            # Run ESLint and save results
            results = run_eslint_on_files(files)
            reformatted_results = reformat_data(results)
            all_results.extend(reformatted_results)

            json_file = f"eslint_results_{project}.json"
            csv_file = f"eslint_results_{project}.csv"
            save_results_to_file(results, reformatted_results, json_file, csv_file)
    # Calculate averages across all projects
    averages = calculate_average_results(all_results)
    # Save average results
    save_averages_to_file(averages, "average_results.json", "average_results.csv")

if __name__ == "__main__":
    main()
