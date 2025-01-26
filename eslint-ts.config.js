import findUnits from "./eslint-plugins/find-units.js";
import firstPlugin from "./eslint-plugins/first-plugin.js";
import LOC from "./eslint-plugins/loc.js";
import noBranches from "./eslint-plugins/no-branches.js";
import containsAsync from "./eslint-plugins/contains-async.js";
import containsDynamicTyping from "./eslint-plugins/contains-dynamic-typing.js";
import containsDomInteraction from "./eslint-plugins/contains-dom.js";
import containsNestedFunction from "./eslint-plugins/contains-nested-function.js";
import containsHigherOrder from "./eslint-plugins/contains-higher-order.js";
import containsCommonJS from "./eslint-plugins/contains-commonjs.js";
import containsClosures from "./eslint-plugins/contains-closures.js";
import containsPrototype from "./eslint-plugins/contains-prototype.js";
import containsPropertyAccess from "./eslint-plugins/contains-property-access.js";
import containsAny from "./eslint-plugins/contains-any.js";
import complexity from "eslint-plugin-complexity";
import tseslint from 'typescript-eslint';
import tsParser from "@typescript-eslint/parser";
// todo better names for rules
export default tseslint.config([
  {
    files: ["**/*.ts", "**/*.tsx"], // Apply to TypeScript files
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: "latest", // Use the latest ECMAScript version
        sourceType: "module", // Use 'module' for ES modules
      },
    },
    plugins: {
      "find-units": findUnits,
      complexity,
      "first-plugin": firstPlugin,
      "LOC": LOC,
      "no-branches": noBranches,
      "contains-async": containsAsync,
      "contains-dynamic-typing": containsDynamicTyping,
      "contains-dom": containsDomInteraction,
      "contains-nested-function": containsNestedFunction,
      "contains-higher-order": containsHigherOrder,
      "contains-commonjs": containsCommonJS,
      "contains-closures": containsClosures,
      "contains-prototype": containsPrototype,
      "contains-property-access": containsPropertyAccess,
      "contains-any": containsAny,
    },
    rules: {
      "find-units/find-units": "warn",   // Contains promise
      "complexity": ["error", { "max": 0 }], // Cyclomatic complexity
      "LOC/LOC": "error", // Lines of code
      "no-branches/count-branches": "error", // Number of branches
      "first-plugin/max-params": ["warn", 1],   // No of params
      "contains-async/find-async": "error",   // Contains asynchronous behaviour
      "contains-dynamic-typing/find-dynamic-typing": "error",   // Contains dynamic typing (let, var, const)
      "contains-dom/find-dom-interaction": "error",   // Contains dom interaction
      "contains-nested-function/find-nested-function": "error",   // Contains a nested function
      "contains-higher-order/find-higher-order": "error",   // Contains a higher order function
      "contains-commonjs/find-commonjs": "error",   // Contains CommonJS
      "contains-closures/find-closures": "error",   // Contains closures
      "contains-prototype/find-prototype": "error",   // Contains prototype usage
      "contains-property-access/find-object-property-access": "error",   // Contains object property access from function parameters
      "contains-any/find-any-usage": "error",   // Contains any usage
    },
  },
]);
