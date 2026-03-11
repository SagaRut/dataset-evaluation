import { getEnclosingContext } from './utils.js';

export default {
  rules: {
    "find-undefined-property-access": {
      meta: {
        type: "problem",
        docs: {
          description: "Detect property accesses that could return 'undefined'.",
        },
        schema: [],
        messages: {
          suspiciousAccess: "Property '{{ prop }}' accessed on object which may not define it, found in {{ enclosingContext }}.",
        },
      },
      create(context) {
        const variableInitMap = new Map();

        return {
          VariableDeclarator(node) {
            if (node.id.type !== 'Identifier') return;
            const varName = node.id.name;
            const init = node.init;

            // Save declared variables (including undefined ones)
            variableInitMap.set(varName, init);
          },

          MemberExpression(node) {
            if (node.computed || node.property.type !== 'Identifier') return;

            const obj = node.object;
            if (obj.type !== 'Identifier') return;

            const varName = obj.name;

            // Only proceed if we've seen a declaration
            if (!variableInitMap.has(varName)) return;

            const init = variableInitMap.get(varName);
            const prop = node.property.name;
            const enclosingContext = getEnclosingContext(node);

            const safeTypes = new Set([
              'ArrayExpression',
              'Literal',
              'ArrowFunctionExpression',
              'FunctionExpression',
              'NewExpression',
              'CallExpression'
            ]);

            // Flag if:
            // - variable is declared with no initializer (undefined)
            // - variable is initialized to an empty object
            if (
              init == null || // undefined or no initializer
              (init.type === 'ObjectExpression' && init.properties.length === 0)
            ) {
              context.report({
                node: node.property,
                messageId: "suspiciousAccess",
                data: {
                  prop,
                  enclosingContext: enclosingContext || "global scope",
                },
              });
            }

            // Otherwise, skip safe inits
            else if (safeTypes.has(init.type)) {
              return;
            }
          }
        };
      }
    }
  }
};
