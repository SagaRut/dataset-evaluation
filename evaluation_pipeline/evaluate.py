import os
import subprocess
import json
import csv
import re

ESLINT_CONFIG = "eslint.config.js"
ESLINT_TYPESCRIPT_CONFIG = "eslint-ts.config.js"
OUTPUT_DIR = "../evaluation_results"
BENCHMARK = "../JS-Projects"

def install_eslint_and_plugins():
    """Ensure ESLint and required plugins are installed."""
    try:
        print("Checking and installing ESLint and plugins...")
        subprocess.run(["npm", "install", "-g", "eslint"], check=True, shell=True)
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
            print(f"Running ESLint on JavaScript file: {file}")
            # Check if the file ends with '.js'
            if file.endswith(".js"):
                print(f"Running ESLint on JavaScript file: {file}")
                result = subprocess.run(
                    ["npx", "eslint", file, "--config", ESLINT_CONFIG, "--format", "json"],
                    capture_output=True,
                    text=True,
                    shell=True
                )
            elif file.endswith(".ts"):
                print(f"Running ESLint on TypeScript file: {file}")
                result = subprocess.run(
                    ["npx", "eslint", file, "--config", ESLINT_TYPESCRIPT_CONFIG, "--format", "json"],
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
                    eslint_result["JS:ES6"] = {}
                    eslint_result["JS:Closures"] = {}
                    eslint_result["JS:Prototype"] = {}
                    eslint_result["JS:PropertyAccess"] = {}
                    eslint_result["JS:WeakTyping"] = {}
                    eslint_result["JS:VariadicParams"] = {}
                    eslint_result["JS:ImplicitGlobals"] = {}
                    eslint_result["JS:Undefined"] = {}
                    eslint_result["JS:ObjectManipulation"] = {}
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
                                        class_list[object.group(1)].append([unit.group(1), message["line"]])
                                    else:
                                        class_list[object.group(1)] = [[unit.group(1), message["line"]]]
                                # Otherwise add the unit name as the key and LOC value as the value
                                eslint_result["LOC"][unit.group(1)] = int(loc.group(1))
                        if message["ruleId"] == "complexity":
                            unit = re.search(r"(?:Function|Method|Static method|Static async method|Getter|Async method)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            cc = re.search(r"complexity of (\d+)", message["message"])
                            if unit and cc:
                                # Add the unit name as the key and CC value as the value
                                eslint_result["CC"][unit.group(1)] = [int(cc.group(1)), message["line"]]
                        # To evaluate on a function level instead of a class level, replace object with property
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
                        if message["ruleId"] == "contains-es6/find-es6-syntax":
                            unit = re.search(r"(?:function|object|variable|class)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:ES6"][unit.group(1)] = 1
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
                        if message["ruleId"] == "contains-weak-typing/find-weak-typing":
                            unit = re.search(r"(?:function|object|variable|class)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:WeakTyping"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-variadic-params/find-variadic-params":
                            unit = re.search(r"(?:function|object|variable|class)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:VariadicParams"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-implicit-globals/find-implicit-globals":
                            unit = re.search(r"(?:function|object|variable|class)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:ImplicitGlobals"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-undefined/find-undefined-property-access":
                            unit = re.search(r"(?:function|object|variable|class)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:Undefined"][unit.group(1)] = 1
                        if message["ruleId"] == "contains-object-manipulation/find-dynamic-object-manipulation":
                            unit = re.search(r"(?:function|object|variable|class)\s+'([a-zA-Z_$][\w$]*)'", message["message"])
                            if unit:
                                # Add the unit name as the key
                                eslint_result["JS:ObjectManipulation"][unit.group(1)] = 1
                    # Set class CC as the average CC of the class methods
                    for class_name, methods in class_list.items():
                        totalCC = 0
                        noMethods = 0
                        for [method, loc] in methods:
                            if method in eslint_result["CC"] and eslint_result["CC"][method] is not None and loc == eslint_result["CC"][method][1]:
                                totalCC = totalCC + eslint_result["CC"][method][0]
                                noMethods = noMethods + 1
                        eslint_result["CC"][class_name] = [totalCC / noMethods if noMethods != 0 else 1, 0]
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
            if loc == 0:
                continue
            cc = result["CC"][unit][0] if unit in result["CC"] and result["CC"][unit][0] != 0 else 1  # Default CC to 1 if not found or if CC is 0
            asyncFound = result["JS:Async"].get(unit, 0)  # Default to 0 if not found
            dynamicTyping = result["JS:DynamicTyping"].get(unit, 0)  # Default to 0 if not found
            domInteraction = result["JS:DomInteraction"].get(unit, 0)  # Default to 0 if not found
            nestedFunction = result["JS:NestedFunction"].get(unit, 0)  # Default to 0 if not found
            higherOrder = result["JS:HigherOrder"].get(unit, 0)  # Default to 0 if not found
            commonJS = result["JS:CommonJS"].get(unit, 0)  # Default to 0 if not found
            es6 = result["JS:ES6"].get(unit, 0)  # Default to 0 if not found
            closures = result["JS:Closures"].get(unit, 0)  # Default to 0 if not found
            prototype = result["JS:Prototype"].get(unit, 0)  # Default to 0 if not found
            propertyAccess = result["JS:PropertyAccess"].get(unit, 0)  # Default to 0 if not found
            weakTyping = result["JS:WeakTyping"].get(unit, 0)  # Default to 0 if not found
            variadicParams = result["JS:VariadicParams"].get(unit, 0)  # Default to 0 if not found
            implicitGlobals = result["JS:ImplicitGlobals"].get(unit, 0)  # Default to 0 if not found
            undefined = result["JS:Undefined"].get(unit, 0)  # Default to 0 if not found
            objectManipulation = result["JS:ObjectManipulation"].get(unit, 0)  # Default to 0 if not found
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
                "JS:ES6": es6,
                "JS:Closures": closures,
                "JS:Prototype": prototype,
                "JS:PropertyAccess": propertyAccess,
                "JS:WeakTyping": weakTyping,
                "JS:VariadicParams": variadicParams,
                "JS:ImplicitGlobals": implicitGlobals,
                "JS:Undefined": undefined,
                "JS:ObjectManipulation": objectManipulation
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
                         "JS:NestedFunction", "JS:HigherOrder", "JS:CommonJS", "JS:ES6",
                         "JS:Closures", "JS:Prototype", "JS:PropertyAccess",
                         "JS:WeakTyping", "JS:VariadicParams", "JS:ImplicitGlobals",
                         "JS:Undefined", "JS:ObjectManipulation"])
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
                result["JS:ES6"],
                result["JS:Closures"],
                result["JS:Prototype"],
                result["JS:PropertyAccess"],
                result["JS:WeakTyping"],
                result["JS:VariadicParams"],
                result["JS:ImplicitGlobals"],
                result["JS:Undefined"],
                result["JS:ObjectManipulation"],
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
        no_of_units = len(metrics["LOC"])
        avg_noJSFeatures = sum(metrics["JSFeatures"]) / len(metrics["JSFeatures"])
        averages.append({"Project": project,
                         "Average LOC": avg_loc,
                         "Average CC": avg_cc,
                         "Number of units": no_of_units,
                         "Average Number of JS Features": avg_noJSFeatures},)

    return averages


def save_averages_to_file(averages, json_file, csv_file):
    """Save averages to JSON and CSV files."""
    # Save to JSON
    with open(os.path.join(OUTPUT_DIR, json_file), "w") as jf:
        json.dump(averages, jf, indent=4)

    # Save to CSV
    with open(os.path.join(OUTPUT_DIR, csv_file), "w", newline="") as cf:
        writer = csv.DictWriter(cf, fieldnames=["Project", "Average LOC", "Average CC", "Number of units", "Average Number of JS Features"])
        writer.writeheader()
        writer.writerows(averages)

def main():
    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Ensure npm packages are installed
    install_eslint_and_plugins()

    all_results = []

    # Extract benchmark name from BENCHMARK path
    benchmark_name = os.path.basename(BENCHMARK.rstrip("/\\"))

    # Iterate over projects in the directory
    for project in os.listdir(BENCHMARK):
        project_path = os.path.join(BENCHMARK, project)
        if os.path.isdir(project_path):
            print(f"Processing project: {project_path}")
            files = []

            for root, dirs, filenames in os.walk(project_path):
                # Modify dirs in-place to skip unwanted folders
                dirs[:] = [d for d in dirs if d not in {'dist', 'test', 'node_modules'}]

                for file in filenames:
                    if file.endswith((".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs")):
                        files.append(os.path.join(root, file))

            print(f"Found {len(files)} files in project: {project_path}")

            # Run ESLint and save results
            results = run_eslint_on_files(project, files)
            reformatted_results = reformat_data(results)
            all_results.extend(reformatted_results)

            json_file = f"eslint_results_{benchmark_name}_{project}.json"
            csv_file = f"eslint_results_{benchmark_name}_{project}.csv"
            save_results_to_file(results, reformatted_results, json_file, csv_file)
    # Calculate averages across all projects
    averages = calculate_average_results(all_results)
    # Save average results
    save_averages_to_file(averages, f"average_results_{benchmark_name}.json", f"average_results_{benchmark_name}.csv")

if __name__ == "__main__":
    main()
