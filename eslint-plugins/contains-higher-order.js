import { getEnclosingContext } from "./utils.js";

export default {
  rules: {
    "find-higher-order": {
      meta: {
        type: "problem",
        docs: {
          description: "Find higher-order functions",
        },
        schema: [],
        messages: {
          found: "Higher-order function detected in '{{ enclosingContext }}'.",
        },
      },
      create(context) {
        function reportHigherOrderFunction(node) {
          const enclosingContext = getEnclosingContext(node);
          context.report({
            node,
            messageId: "found",
            data: { enclosingContext: enclosingContext || "global scope" },
          });
        }

        // Detects if the function calls one of its parameters
        // Covers: function doSomething(callback) { callback(); }
        function hasFunctionParameter(node) {
          const paramNames = new Set(
            node.params
              .filter(param => param.type === "Identifier")
              .map(param => param.name)
          );

          let found = false;

          function checkCalls(n) {
            if (
              n.type === "CallExpression" &&
              n.callee.type === "Identifier" &&
              paramNames.has(n.callee.name)
            ) {
              found = true;
            }
          }

          // Traverse the function body to find calls to parameters
          context.getSourceCode().visitorKeys[node.body.type].forEach(key => {
            const bodyNodes = node.body[key];
            if (Array.isArray(bodyNodes)) {
              bodyNodes.forEach(child => context.parserServices?.esTreeNodeToTSNodeMap ? traverse(child) : checkCalls(child));
            } else if (bodyNodes) {
              context.parserServices?.esTreeNodeToTSNodeMap ? traverse(bodyNodes) : checkCalls(bodyNodes);
            }
          });

          function traverse(n) {
            if (found) return;
            checkCalls(n);
            const keys = context.getSourceCode().visitorKeys[n.type] || [];
            keys.forEach(k => {
              const child = n[k];
              if (Array.isArray(child)) {
                child.forEach(traverse);
              } else if (child) {
                traverse(child);
              }
            });
          }

          traverse(node.body);
          return found;
        }

        // Detects if a function is passed as an argument to a function call
        // Covers: setTimeout(() => {}, 1000), or fn(function() {})
        function isHigherOrderFunctionArgument(node) {
          return (
            node.arguments &&
            node.arguments.some(
              (arg) =>
                arg.type === "FunctionExpression" ||
                arg.type === "ArrowFunctionExpression"
            )
          );
        }

        // Detects if a function directly returns a function
        // Covers: return function() { ... }, or return () => { ... }
        function isHigherOrderFunctionReturn(node) {
          let found = false;

          function checkReturn(n) {
            if (found) return;

            if (n.type === "ReturnStatement") {
              const ret = n.argument;
              if (
                ret &&
                (ret.type === "FunctionExpression" ||
                 ret.type === "ArrowFunctionExpression")
              ) {
                found = true;
              }
            }
          }

          function traverse(n) {
            if (!n || found) return;
            checkReturn(n);

            const keys = context.getSourceCode().visitorKeys[n.type] || [];
            keys.forEach(key => {
              const child = n[key];
              if (Array.isArray(child)) {
                child.forEach(traverse);
              } else if (child) {
                traverse(child);
              }
            });
          }

          if (node.body.type === "BlockStatement") {
            traverse(node.body);
          }

          return found;
        }


        return {
          // Checks calls like: setTimeout(() => {}, 1000)
          CallExpression(node) {
            if (isHigherOrderFunctionArgument(node)) {
              reportHigherOrderFunction(node);
            }
          },
          // Checks function declarations:
          // - if they call a function parameter (callback pattern)
          // - if they return a function directly
          FunctionDeclaration(node) {
            if (hasFunctionParameter(node) || isHigherOrderFunctionReturn(node)) {
              reportHigherOrderFunction(node);
            }
          },
          // Same for function expressions (e.g., const f = function() {...})
          FunctionExpression(node) {
            if (hasFunctionParameter(node) || isHigherOrderFunctionReturn(node)) {
              reportHigherOrderFunction(node);
            }
          },
          // Specifically detects arrow functions that return another function
          // Covers: const f = () => () => 42;
          ArrowFunctionExpression(node) {
            if (
              node.body.type === "FunctionExpression" ||
              node.body.type === "ArrowFunctionExpression"
            ) {
              reportHigherOrderFunction(node);
            }
          },
        };
      },
    },
  },
};
