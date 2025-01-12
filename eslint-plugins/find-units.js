export default {
  rules: {
    "find-units": {
      meta: {
        type: "suggestion",
        docs: {
          description: "Detect exported units in a file (ESM and CommonJS)",
          category: "Best Practices",
        },
        schema: [], // No options
      },
      create(context) {
        const reportExport = (node, exportType, name) => {
          context.report({
            node,
            message: `${exportType} export found: ${name}`,
          });
        };

        return {
          ExportNamedDeclaration(node) {
            const name =
              node.declaration?.id?.name || // For named exports like `export const x = ...`
              node.declaration?.declarations?.[0]?.id?.name || // For `export let/const/var x = ...`
              "anonymous";
            reportExport(node, "Named", name);
          },

          ExportDefaultDeclaration(node) {
            const name =
              node.declaration?.id?.name || // For `export default function x() {}` or `export default class X {}`
              (node.declaration.type === "Identifier"
                ? node.declaration.name // For `export default x`
                : "anonymous");
            reportExport(node, "Default", name);
          },

          AssignmentExpression(node) {
            if (
              node.left.type === "MemberExpression" &&
              node.left.object.name === "module" &&
              node.left.property.name === "exports"
            ) {
              // Detect `module.exports = ...`
              const name =
                node.right.type === "Identifier"
                  ? node.right.name // For `module.exports = View;`
                  : node.right.type === "FunctionExpression" ||
                    node.right.type === "ArrowFunctionExpression"
                  ? node.right.id?.name || "anonymous function"
                  : null;
              if (name) {
                reportExport(node, "CommonJS", name);
              }
            } else if (
              node.left.type === "MemberExpression" &&
              node.left.object.name === "exports"
            ) {
              // Detect `exports.something = ...`
              const propertyName = node.left.property.name || "unknown";
              const rightName =
                node.right.type === "FunctionExpression" ||
                node.right.type === "ArrowFunctionExpression"
                  ? node.right.id?.name || `anonymous function`
                  : null;
              if (rightName) {
                reportExport(
                  node,
                  "CommonJS",
                  `${propertyName} (${rightName})`
                );
              }
            }
          },

          VariableDeclarator(node) {
            // Handle cases like: `exports.compileETag = function(val) { ... }`
            if (
              node.init &&
              node.init.type === "FunctionExpression" &&
              node.id.type === "MemberExpression" &&
              node.id.object.name === "exports"
            ) {
              const propertyName = node.id.property.name || null;
              if (propertyName) {
                reportExport(node, "CommonJS", propertyName);
              }
            }
          },

          FunctionDeclaration(node) {
            // Handle cases like: `function View(name, options) { ... }` followed by `module.exports = View;`
            const parent = node.parent;
            if (
              parent &&
              parent.type === "Program" &&
              parent.body.some(
                (stmt) =>
                  stmt.type === "ExpressionStatement" &&
                  stmt.expression.type === "AssignmentExpression" &&
                  stmt.expression.left.type === "MemberExpression" &&
                  stmt.expression.left.object.name === "module" &&
                  stmt.expression.left.property.name === "exports" &&
                  stmt.expression.right.type === "Identifier" &&
                  stmt.expression.right.name === node.id.name
              )
            ) {
              reportExport(node, "CommonJS", node.id.name);
            }
          },
        };
      },
    },
  },
};
