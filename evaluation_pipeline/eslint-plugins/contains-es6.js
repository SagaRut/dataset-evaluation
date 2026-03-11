import { getEnclosingContext } from './utils.js';

export default {
  rules: {
    "find-es6-syntax": {
      meta: {
        type: "suggestion", // This rule is a suggestion, not necessarily a code problem
        docs: {
          description: "Detect usage of ES6+ features: let/const, import/export, arrow functions.",
        },
        schema: [], // No options needed for this rule
        messages: {
          es6Feature: "ES6+ feature '{{ type }}' used in '{{ enclosingContext }}'.", // Message template for reports
        },
      },
      create(context) {
        return {
          // Detect usage of `let` or `const` declarations
          VariableDeclaration(node) {
            if (node.kind === "let" || node.kind === "const") {
              const enclosingContext = getEnclosingContext(node);
              context.report({
                node,
                messageId: "es6Feature",
                data: { type: node.kind, enclosingContext: enclosingContext || "global scope" },
              });
            }
          },
          // Detect usage of ES6 `import` statements
          ImportDeclaration(node) {
            const enclosingContext = getEnclosingContext(node);
            context.report({
              node,
              messageId: "es6Feature",
              data: { type: "import", enclosingContext: enclosingContext || "global scope" },
            });
          },
          // Detect named export declarations (e.g., `export { x }`)
          ExportNamedDeclaration(node) {
            const enclosingContext = getEnclosingContext(node);
            context.report({
              node,
              messageId: "es6Feature",
              data: { type: "export", enclosingContext: enclosingContext || "global scope" },
            });
          },
          // Detect default export declarations (e.g., `export default x`)
          ExportDefaultDeclaration(node) {
            const enclosingContext = getEnclosingContext(node);
            context.report({
              node,
              messageId: "es6Feature",
              data: { type: "export default", enclosingContext: enclosingContext || "global scope" },
            });
          },
          // Detect arrow function expressions (e.g., `() => {}`)
          ArrowFunctionExpression(node) {
            const enclosingContext = getEnclosingContext(node);
            context.report({
              node,
              messageId: "es6Feature",
              data: { type: "arrow function", enclosingContext: enclosingContext || "global scope" },
            });
          },
        };
      },
    },
  },
};