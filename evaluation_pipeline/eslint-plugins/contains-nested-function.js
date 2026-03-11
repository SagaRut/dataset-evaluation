import { getEnclosingContext } from './utils.js';

// TODO fara yfir closures og nested function dectectionin...
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
          found: "Nested function found in '{{ enclosingContext }}'.",
        },
      },
      create(context) {
        function reportNestedFunction(node) {
          const enclosingContext = getEnclosingContext(node);
          context.report({
            node,
            messageId: "found",
            data: { enclosingContext: enclosingContext || "global scope" },
          });
        }

        return {
          FunctionDeclaration(node) {
            const enclosingContext = getEnclosingContext(node);
            if (enclosingContext.includes(">")) {
              reportNestedFunction(node);
            }
          },
          FunctionExpression(node) {
            const enclosingContext = getEnclosingContext(node);
            if (enclosingContext.includes(">")) {
              reportNestedFunction(node);
            }
          },
          ArrowFunctionExpression(node) {
            const enclosingContext = getEnclosingContext(node);
            if (enclosingContext.includes(">")) {
              reportNestedFunction(node);
            }
          },
        };
      },
    },
  },
};
