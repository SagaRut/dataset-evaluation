import { getEnclosingContexts } from './utils.js';

export default {
  rules: {
    "find-nested-function": {
      meta: {
        type: "problem",
        docs: {
          description: "Find nested functions",
        },
        schema: [],
        messages: {
          found: "Nested function found in '{{ contexts }}'.",
        },
      },
      create(context) {
        function reportNestedFunction(node) {
          const contexts = getEnclosingContexts(node);
          context.report({
            node,
            messageId: "found",
            data: { contexts: contexts || "global scope" },
          });
        }

        return {
          FunctionDeclaration(node) {
            const contexts = getEnclosingContexts(node);
            if (contexts.includes(">")) {
              reportNestedFunction(node);
            }
          },
          FunctionExpression(node) {
            const contexts = getEnclosingContexts(node);
            if (contexts.includes(">")) {
              reportNestedFunction(node);
            }
          },
          ArrowFunctionExpression(node) {
            const contexts = getEnclosingContexts(node);
            if (contexts.includes(">")) {
              reportNestedFunction(node);
            }
          },
        };
      },
    },
  },
};
