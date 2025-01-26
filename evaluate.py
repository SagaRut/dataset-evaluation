import os
import subprocess
import json
import csv
import re

# Path to the ESLint config file
ESLINT_CONFIG = "eslint.config.js"
OUTPUT_DIR = "results"

# Only evaluate units that are exported
# Todo how to evaluate cyclomatic complexity of units that are exported classes?
# Todo How does the llm eval plugin find units, also classes??
# Todo setup JS feature
# TODO rest of JS features, finna instance, fyrst og gera evaluation á complexity miðað við það/coverage af hlutum?
# TODO rest af hlutum sem Mitchell talaði um
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
        # npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
        print("Installing the typescript parser.")
        subprocess.run(["npm", "install", "eslint", "@typescript-eslint/parser", "--save-dev"], check=True, shell=True)
        print("Installing the complexity plugin.")
        subprocess.run(["npm", "install", "eslint-plugin-complexity", "--save-dev"], check=True, shell=True)
        print("ESLint and plugins installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing ESLint or plugins: {e}")
        exit(1)

def run_eslint_on_files(project, files):
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

                    # Add the project path and file name to the result
                    eslint_result["project"] = project
                    eslint_result["fileName"] = file
                    eslint_result["exportedUnits"] = []
                    eslint_result["LOC"] = {}
                    eslint_result["CC"] = {}
                    eslint_result["JS:Async"] = {}
                    eslint_result["JS:DynamicTyping"] = {}
                    eslint_result["JS:DomInteraction"] = {}
                    eslint_result["JS:NestedFunction"] = {}
                    eslint_result["JS:HigherOrder"] = {}
                    eslint_result["JS:CommonJS"] = {}
                    eslint_result["JS:Closures"] = {}
                    eslint_result["JS:Prototype"] = {}
                    eslint_result["JS:PropertyAccess"] = {}
                    eslint_result["TS:Any"] = {}
                    class_list = {}

                    # Find exported units
                    for message in eslint_result["messages"]:
                        # Find exported units
                        if message["ruleId"] == "find-units/find-units":
                            unit = re.search(r"found:\s+([a-zA-Z_$][\w$]*)", message["message"])
                            commonJS = re.search(r"CommonJS", message["message"])
                            if unit:
                                # Append the matched unit to the list
                                eslint_result["exportedUnits"].append(unit.group(1))
                                if commonJS:
                                    eslint_result["JS:CommonJS"][unit.group(1)] = 1
                        if message["ruleId"] == "LOC/LOC":
                            unit = re.search(r"Unit\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            loc = re.search(r"has (\d+)", message["message"])
                            object = re.search(r"object\s+'([a-zA-Z_$][\w$]*)", message["message"])
                            if unit and loc:
                                # If the unit is linked to an object add the loc to the object loc
                                if object:
                                    current_loc = eslint_result["LOC"].get(object.group(1), 0)
                                    eslint_result["LOC"][object.group(1)] = current_loc + int(loc.group(1))
                                    # Add class and corresponding method to list
                                    if object.group(1) in class_list:
                                        class_list[object.group(1)].append(unit.group(1))
                                    else:
                                        class_list[object.group(1)] = [unit.group(1)]
                                # Otherwise add the unit name as the key and LOC value as the value
                                eslint_result["LOC"][unit.group(1)] = int(loc.group(1))
                        if message["ruleId"] == "complexity":
                            unit = re.search(r"(?:Function|Method)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            cc = re.search(r"complexity of (\d+)", message["message"])
                            if unit and cc:
                                # Add the unit name as the key and CC value as the value
                                eslint_result["CC"][unit.group(1)] = int(cc.group(1))
                        if message["ruleId"] == "contains-async/find-async":
                            unit = re.search(r"(?:function|object|variable|class)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:Async"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-dynamic-typing/find-dynamic-typing":
                            unit = re.search(r"(?:function|object|variable|class)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:DynamicTyping"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-dom/find-dom-interaction":
                            unit = re.search(r"(?:function|object|variable|class)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:DomInteraction"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-nested-function/find-nested-function":
                            unit = re.search(r"(?:function|object|variable|class)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:NestedFunction"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-higher-order/find-higher-order":
                            unit = re.search(r"(?:function|object|variable|class)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:HigherOrder"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-commonjs/find-commonjs":
                            unit = re.search(r"(?:function|object|variable|class)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:CommonJS"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-closures/find-closures":
                            unit = re.search(r"(?:function|object|variable)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:Closures"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-prototype/find-prototype":
                            unit = re.search(r"(?:function|object|variable|class)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:Prototype"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-property-access/find-object-property-access":
                            unit = re.search(r"(?:function|object|variable|class)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:PropertyAccess"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-any/find-any":
                            unit = re.search(r"(?:function|object|variable|class)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["TS:Any"][unit.group(1)] = 1
                    # Set class CC as the average CC of the class methods
                    for class_name, methods in class_list.items():
                        totalCC = 0
                        for method in methods:
                            if method in eslint_result["CC"] and eslint_result["CC"][method] is not None:
                                totalCC = totalCC + eslint_result["CC"][method]
                        eslint_result["CC"][class_name] = totalCC/len(methods)
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
            cc = result["CC"].get(unit, 1)  # Default CC to 1 if not found
            asyncFound = result["JS:Async"].get(unit, 0)  # Default to 0 if not found
            dynamicTyping = result["JS:DynamicTyping"].get(unit, 0)  # Default to 0 if not found
            domInteraction = result["JS:DomInteraction"].get(unit, 0)  # Default to 0 if not found
            nestedFunction = result["JS:NestedFunction"].get(unit, 0)  # Default to 0 if not found
            higherOrder = result["JS:HigherOrder"].get(unit, 0)  # Default to 0 if not found
            commonJS = result["JS:CommonJS"].get(unit, 0)  # Default to 0 if not found
            closures = result["JS:Closures"].get(unit, 0)  # Default to 0 if not found
            prototype = result["JS:Prototype"].get(unit, 0)  # Default to 0 if not found
            propertyAccess = result["JS:PropertyAccess"].get(unit, 0)  # Default to 0 if not found
            any = result["TS:Any"].get(unit, 0)  # Default to 0 if not found
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
                "JS:HigherOrder": higherOrder,
                "JS:CommonJS": commonJS,
                "JS:Closures": closures,
                "JS:Prototype": prototype,
                "JS:PropertyAccess": propertyAccess,
                "TS:Any": any
            })
    return json_data

def save_results_to_file(results, reformatted_results, json_file, csv_file):
    """Save ESLint results to JSON and CSV files."""
    with open(os.path.join(OUTPUT_DIR, json_file), "w") as f:
        json.dump(results, f, indent=4)
    print(f"Results saved to {json_file}")

    with open(os.path.join(OUTPUT_DIR, csv_file), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Project", "File", "Unit", "LOC", "CC",
                         "JS:Async", "JS:DynamicTyping", "JS:DomInteraction",
                         "JS:NestedFunction", "JS:HigherOrder", "JS:CommonJS",
                         "JS:Closures", "JS:Prototype", "JS:PropertyAccess", "TS:Any"])
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
                result["JS:CommonJS"],
                result["JS:Closures"],
                result["JS:Prototype"],
                result["JS:PropertyAccess"],
                result["TS:Any"],
            ])
    print(f"Results saved to {csv_file}")


def calculate_average_results(results):
    """Calculate average LOC and CC per project."""
    project_data = {}

    # Group results by project
    for result in results:
        project = result["Project"]
        loc = result["LOC"]
        cc = result["CC"]
        noOfJSFeatures = sum(value for key, value in result.items() if key.startswith('JS'))
        noOfTSFeatures = sum(value for key, value in result.items() if key.startswith('TS'))

        if project not in project_data:
            project_data[project] = {"LOC": [], "CC": [], "JSFeatures": [], "TSFeatures": []}

        project_data[project]["LOC"].append(loc)
        project_data[project]["CC"].append(cc)
        project_data[project]["JSFeatures"].append(noOfJSFeatures)
        project_data[project]["TSFeatures"].append(noOfTSFeatures)

    # Calculate averages
    averages = []
    for project, metrics in project_data.items():
        avg_loc = sum(metrics["LOC"]) / len(metrics["LOC"])
        avg_cc = sum(metrics["CC"]) / len(metrics["CC"])
        avg_noJSFeatures = sum(metrics["JSFeatures"]) / len(metrics["JSFeatures"])
        avg_noTSFeatures = sum(metrics["TSFeatures"]) / len(metrics["TSFeatures"])
        averages.append({"Project": project,
                         "Average LOC": avg_loc,
                         "Average CC": avg_cc,
                         "Average Number of JS Features": avg_noJSFeatures,
                         "Average Number of TS Features": avg_noTSFeatures},)

    return averages


def save_averages_to_file(averages, json_file, csv_file):
    """Save averages to JSON and CSV files."""
    # Save to JSON
    with open(os.path.join(OUTPUT_DIR, json_file), "w") as jf:
        json.dump(averages, jf, indent=4)

    # Save to CSV
    with open(os.path.join(OUTPUT_DIR, csv_file), "w", newline="") as cf:
        writer = csv.DictWriter(cf, fieldnames=["Project", "Average LOC", "Average CC", "Average Number of JS Features", "Average Number of TS Features"])
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
                for file in filenames if (file.endswith(".js") or file.endswith(".ts"))
            ]
            print(f"Found {len(files)} files in project: {project_path}")

            # Run ESLint and save results
            results = run_eslint_on_files(project, files)
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
