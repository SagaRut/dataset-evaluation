import { getEnclosingContext } from './utils.js';
import { findVariable } from 'eslint-utils';

export default {
  rules: {
    "find-closures": {
      meta: {
        type: "problem",
        docs: {
          description: "Detect closures: functions accessing outer scope variables.",
        },
        schema: [],
        messages: {
          found: "Closure detected in '{{ enclosingContext }}', accessing '{{ name }}' from an outer scope.",
        },
      },
      create(context) {
        // Scope manager to track variable scope hierarchy
        const scopeManager = context.getSourceCode().scopeManager;

        // Stack of function scopes entered
        const functionScopes = [];

        // Push the current function's scope when entering a function
        function enterFunction(node) {
          const scope = scopeManager.acquire(node);
          functionScopes.push(scope);
        }

        // Pop the function's scope when exiting the function
        function exitFunction() {
          functionScopes.pop();
        }

        return {
          // Track all function types
          FunctionDeclaration: enterFunction,       // Example: function foo() {}
          FunctionExpression: enterFunction,        // Example: const f = function() {}
          ArrowFunctionExpression: enterFunction,   // Example: const f = () => {}

          // Exit handlers to pop the scope when function ends
          'FunctionDeclaration:exit': exitFunction,
          'FunctionExpression:exit': exitFunction,
          'ArrowFunctionExpression:exit': exitFunction,

          // Identifier handler checks for outer scope variable access
          Identifier(node) {
            // Need at least two nested scopes to form a closure
            if (functionScopes.length < 2) return;

            const currentScope = functionScopes[functionScopes.length - 1];  // Innermost function
            const outerScope = functionScopes[functionScopes.length - 2];    // Immediate outer function

            // Find the variable associated with this identifier
            const variable = findVariable(currentScope, node);
            if (!variable) return;

            // Ignore declarations (we only want references)
            if (
              (node.parent.type === "VariableDeclarator" && node.parent.id === node) ||  // var x = ...
              (node.parent.type === "FunctionDeclaration" && node.parent.id === node) || // function x() {}
              (node.parent.type === "FunctionExpression" && node.parent.id === node)     // const x = function x() {}
            ) {
              return;
            }

            // If the variable is declared in the outer function scope, it's a closure
            if (outerScope.variables.includes(variable)) {
              const enclosingContext = getEnclosingContext(node);
              context.report({
                node,
                messageId: "found",
                data: {
                  name: node.name,
                  enclosingContext: enclosingContext || "global scope",
                },
              });
            }
          }
        };
      },
    },
  },
};
