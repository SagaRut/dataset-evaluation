import findUnits from "./eslint-plugins/find-units.js";
import LOC from "./eslint-plugins/loc.js";
import noBranches from "./eslint-plugins/no-branches.js";
import containsAsync from "./eslint-plugins/contains-async.js";
import containsDynamicTyping from "./eslint-plugins/contains-dynamic-typing.js";
import containsDomInteraction from "./eslint-plugins/contains-dom.js";
import containsNestedFunction from "./eslint-plugins/contains-nested-function.js";
import containsHigherOrder from "./eslint-plugins/contains-higher-order.js";
import containsCommonJS from "./eslint-plugins/contains-commonjs.js";
import containsES6 from "./eslint-plugins/contains-es6.js";
import containsClosures from "./eslint-plugins/contains-closures.js";
import containsPrototype from "./eslint-plugins/contains-prototype.js";
import containsPropertyAccess from "./eslint-plugins/contains-property-access.js";
import containsWeakTyping from "./eslint-plugins/contains-weak-typing.js";
import containsVariadicParams from "./eslint-plugins/contains-variadic-params.js";
import containsImplicitGlobals from "./eslint-plugins/contains-implicit-globals.js";
import containsUndefined from "./eslint-plugins/contains-undefined.js";
import containsObjectManipulation from "./eslint-plugins/contains-object-manipulation.js";
import complexity from "eslint-plugin-complexity";

export default [
  {
    plugins: {
      "find-units": findUnits,
      complexity,
      "LOC": LOC,
      "no-branches": noBranches,
      "contains-async": containsAsync,
      "contains-dynamic-typing": containsDynamicTyping,
      "contains-dom": containsDomInteraction,
      "contains-nested-function": containsNestedFunction,
      "contains-higher-order": containsHigherOrder,
      "contains-commonjs": containsCommonJS,
      "contains-es6": containsES6,
      "contains-closures": containsClosures,
      "contains-prototype": containsPrototype,
      "contains-property-access": containsPropertyAccess,
      "contains-weak-typing": containsWeakTyping,
      "contains-variadic-params": containsVariadicParams,
      "contains-implicit-globals": containsImplicitGlobals,
      "contains-undefined": containsUndefined,
      "contains-object-manipulation": containsObjectManipulation,
    },
    rules: {
      "find-units/find-units": "warn",   // Find units
      "complexity": ["error", { "max": 0 }], // Cyclomatic complexity
      "LOC/LOC": "error", // Lines of code
      "no-branches/count-branches": "error", // Number of branches
      "contains-async/find-async": "error",   // Contains asynchronous behaviour
      "contains-dynamic-typing/find-dynamic-typing": "error",   // Contains dynamic typing (let, var, const)
      "contains-dom/find-dom-interaction": "error",   // Contains dom interaction
      "contains-nested-function/find-nested-function": "error",   // Contains a nested function
      "contains-higher-order/find-higher-order": "error",   // Contains a higher order function
      "contains-commonjs/find-commonjs": "error",   // Contains CommonJS
      "contains-es6/find-es6-syntax": "error",   // Contains ES6 syntax
      "contains-closures/find-closures": "error",   // Contains closures
      "contains-prototype/find-prototype": "error",   // Contains prototype usage
      "contains-property-access/find-object-property-access": "error",   // Contains object property access from function parameters
      "contains-weak-typing/find-weak-typing": "error", // Contains examples of weak typing
      "contains-variadic-params/find-variadic-params": "error", // Contains examples of non-fixed function parameters
      "contains-implicit-globals/find-implicit-globals": "error", // Contains examples of implicit globals
      "contains-undefined/find-undefined-property-access": "error", // Contains examples of undefined property access
      "contains-object-manipulation/find-dynamic-object-manipulation": "error", // Contains examples of dynamic object manipulation
    },
  },
];
