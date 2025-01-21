export default {
  rules: {
    "LOC": {
      meta: {
        type: "problem",
        docs: {
          description: "Report the number of lines of code in a function or object",
        },
        schema: [],
        messages: {
          loc: "Unit '{{ name }}' has {{ loc }} lines of code and is linked to object '{{ object }}'.",
        },
      },
      create(context) {
        function reportLOC(node, name, object = null) {
          const loc = node.loc.end.line - node.loc.start.line + 1;
          const data = { name, loc,
              object: object || "", // If object is null, use an empty string
              };
          context.report({
            node,
            messageId: "loc",
            data,
          });
        }

        function getParentObject(node) {
          if (
            node.parent &&
            node.parent.type === "AssignmentExpression" &&
            node.parent.left.type === "MemberExpression"
          ) {
            const objectNode = node.parent.left.object;
            if (objectNode.type === "Identifier") {
              return objectNode.name; // e.g., "res"
            }
          }
          return null;
        }

        return {
          // For function declarations
          FunctionDeclaration(node) {
            const functionName = node.id ? node.id.name : "anonymous";
            reportLOC(node, functionName);
          },
          // For classes
          ClassDeclaration(node) {
            const className = node.id ? node.id.name : "anonymous";
            reportLOC(node, className);
          },
          // For variable declarations (e.g., var req = Object.create(...))
          VariableDeclarator(node) {
            if (node.init && node.id.type === "Identifier") {
              const variableName = node.id.name;
              reportLOC(node, variableName);
            }
          },
          // For assignment expressions like `module.exports = function ...`
          AssignmentExpression(node) {
            if (node.right) {
              if (
                node.right.type === "FunctionExpression" ||
                node.right.type === "ArrowFunctionExpression"
              ) {
                const parentObject = getParentObject(node.right);
                const functionName =
                  node.right.id?.name || // Named function expressions
                  (node.left.type === "MemberExpression" && node.left.property.name) ||
                  "anonymous";
                reportLOC(node.right, functionName, parentObject);
              }
            }
          },
          // For functions assigned as properties (e.g., `res.someFunction = function ...`)
          FunctionExpression(node) {
            const parentObject = getParentObject(node);
            const functionName = node.id ? node.id.name : "anonymous";
            if (parentObject) {
              reportLOC(node, functionName, parentObject);
            }
          },
          ArrowFunctionExpression(node) {
            const parentObject = getParentObject(node);
            const functionName = node.id ? node.id.name : "anonymous";
            if (parentObject) {
              reportLOC(node, functionName, parentObject);
            }
          },
        };
      },
    },
  },
};
