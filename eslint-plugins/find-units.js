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
          // Covers export { foo, bar }
          // Covers export const foo = () => {...}
          // Covers export function foo() {...}
          ExportNamedDeclaration(node) {
            if (node.declaration) {
              if (node.declaration.type === "VariableDeclaration") {
                // Handle `export const foo = () => {...}` and similar cases
                node.declaration.declarations.forEach((decl) => {
                  if (decl.id.type === "Identifier") {
                    // Check if the initializer is a function or callable
                    const isFunction =
                      decl.init &&
                      (decl.init.type === "ArrowFunctionExpression" ||
                       decl.init.type === "FunctionExpression");

                    // Only report if the initializer is a function
                    if (isFunction) {
                      reportExport(node, "Named", decl.id.name);
                    }
                  }
                });
              } else if (node.declaration.type === "FunctionDeclaration") {
                // Handle `export function foo() {...}`
                reportExport(node, "Named", node.declaration.id.name);
              }
            } else if (node.specifiers) {
              // Handle `export { foo, bar }`
              node.specifiers.forEach((specifier) => {
                const name = specifier.exported.name;
                reportExport(node, "Named", name);
              });
            }
          },
          // Covers export default foo
          ExportDefaultDeclaration(node) {
            const name =
              node.declaration?.id?.name || // For `export default function x() {}` or `export default class X {}`
              (node.declaration.type === "Identifier"
                ? node.declaration.name // For `export default x`
                : "anonymous");
            reportExport(node, "Default", name);
          },
          // Covers exports.foo = ...
          // Covers module.exports = ...
          // Covers ... = exports
          // Covers ... = module.exports
          AssignmentExpression(node) {
            if (
              node.left.type === "MemberExpression" &&
              node.left.object.name === "module" &&
              node.left.property.name === "exports"
            ) {
              // Handle `module.exports = ...`
              const name =
                node.right.type === "Identifier"
                  ? node.right.name
                  : node.right.type === "FunctionExpression" ||
                    node.right.type === "ArrowFunctionExpression"
                  ? node.right.id?.name || "anonymous function"
                  : null; // Skip non-function types

              // Only report if a named export is found
              if (name) {
                reportExport(node, "CommonJS", name);
              }
            } else if (
              node.left.type === "MemberExpression" &&
              node.left.object.name === "exports"
            ) {
              // Handle `exports.foo = ...` or `exports.compileETag = ...`
              const propertyName = node.left.property.name;
              let rightName = null;

              if (node.right.type === "Identifier") {
                rightName = node.right.name; // Extract named identifier
              } else if (
                node.right.type === "FunctionExpression" ||
                node.right.type === "ArrowFunctionExpression"
              ) {
                rightName = node.right.id ? node.right.id.name : "anonymous function"; // Handle function assignment
              }

              // Report the export only if a function or named identifier is found
              if (rightName) {
                reportExport(node, "CommonJS", `${propertyName} (${rightName})`);
              }
            } else if (
              node.right.type === "MemberExpression" &&
              node.right.object.name === "module" &&
              node.right.property.name === "exports"
            ) {
              // Handle `... = module.exports`
              const name =
                node.left.type === "Identifier"
                  ? node.left.name
                  : node.left.type === "MemberExpression" &&
                    node.left.object.name === "exports"
                  ? `${node.left.object.name}.${node.left.property.name}`
                  : null; // Skip anonymous exports

              // Only report if a named export is found
              if (name) {
                reportExport(node, "CommonJS", `${name} (alias of module.exports)`);
              }
            } else if (
              node.right.type === "Identifier" &&
              node.right.name === "exports"
            ) {
              // Handle `... = exports`
              const name =
                node.left.type === "Identifier"
                  ? node.left.name
                  : node.left.type === "MemberExpression"
                  ? `${node.left.object.name}.${node.left.property.name}`
                  : null; // Skip anonymous exports

              // Only report if a named export is found
              if (name) {
                reportExport(node, "CommonJS", `${name} (alias of exports)`);
              }
            }
          },
          // Covers var ... = exports
          // Covers var ... = module.exports
          VariableDeclarator(node) {
            // Detect any assignment where `... = exports` or `... = module.exports`
            if (
              node.init && (
                // Right side is `exports`
                (node.init.type === "Identifier" && node.init.name === "exports") ||
                // Right side is `module.exports`
                (node.init.type === "MemberExpression" &&
                  node.init.object.type === "Identifier" &&
                  node.init.object.name === "module" &&
                  node.init.property.type === "Identifier" &&
                  node.init.property.name === "exports")
              ) &&
              node.id.type === "Identifier" && // Left side is a variable
              node.id.name // Ensure the variable name exists (e.g., "app")
            ) {
              const variableName = node.id.name;
              reportExport(node, "CommonJS", variableName);
            }
          },
        };
      },
    },
  },
};
