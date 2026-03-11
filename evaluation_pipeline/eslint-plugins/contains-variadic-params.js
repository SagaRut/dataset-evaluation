import { getEnclosingContext } from './utils.js';

export default {
  rules: {
    "find-variadic-params": {
      meta: {
        type: "problem",
        docs: {
          description: "Detect non-fixed function parameters (arguments object or rest parameters)",
        },
        schema: [],
        messages: {
          foundArguments: "Use of 'arguments' object found in '{{ enclosingContext }}'.",
          foundRest: "Use of rest parameters (...args) found in '{{ enclosingContext }}'.",
        },
      },
      create(context) {
        return {
          // Detect usage of the `arguments` object in functions
          Identifier(node) {
            if (node.name !== "arguments") return;

            // Ignore cases where `arguments` is used as a property key (e.g., obj.arguments)
            const parent = node.parent;
            if (
              (parent?.type === "Property" && parent.key === node && !parent.computed) ||
              (parent?.type === "MemberExpression" && parent.property === node && !parent.computed)
            ) {
              return;
            }

            // Report use of the `arguments` object with context information
            const enclosingContext = getEnclosingContext(node);
            context.report({
              node,
              messageId: "foundArguments",
              data: { enclosingContext: enclosingContext || "global scope" },
            });
          },

          // Detect use of rest parameters (e.g., ...args)
          RestElement(node) {
            const enclosingContext = getEnclosingContext(node);
            context.report({
              node,
              messageId: "foundRest",
              data: { enclosingContext: enclosingContext || "global scope" },
            });
          }
        };
      }
    }
  }
};
