import { getEnclosingContext } from './utils.js';
export default {
  rules: {
    'find-weak-typing': {
      meta: {
        type: 'problem',
        docs: {
          description: 'Find cases of permissive and weak typing',
        },
        schema: [],
        messages: {
          stringConcat: "Possible implicit string coercion: '{{ left }} + {{ right }}' becomes a string found in '{{ enclosingContext }}'",
          unaryCoercion: "Unary coercion detected: '{{ op }}{{ value }}' found in '{{ enclosingContext }}'",
          bitwiseCoercion: "Bitwise coercion detected: '{{ expr }} | 0' found in '{{ enclosingContext }}' ",
          conditionalCoercion: "Conditional coercion with '{{ test }}' (truthy/falsy behavior might be unclear) found in '{{ enclosingContext }}'",
          looseEquality: "Loose equality detected: '{{ left }} == {{ right }}'. Consider using '===' found in '{{ enclosingContext }}'",
        },
      },
      create(context) {
        return {
          BinaryExpression(node) {
            // Detect string + anything
            if (node.operator === '+' &&
                (node.left.type === 'Literal' && typeof node.left.value === 'string' ||
                 node.right.type === 'Literal' && typeof node.right.value === 'string')) {
                const enclosingContext = getEnclosingContext(node);
                context.report({
                node,
                messageId: 'stringConcat',
                data: {
                  left: context.getSourceCode().getText(node.left),
                  right: context.getSourceCode().getText(node.right),
                  enclosingContext: enclosingContext || "global scope"
                },
              });
            }

            // Detect bitwise coercion (e.g., value | 0)
            if (node.operator === '|' &&
                (node.right.type === 'Literal' && node.right.value === 0)) {
              const enclosingContext = getEnclosingContext(node);
              context.report({
                node,
                messageId: 'bitwiseCoercion',
                data: {
                  expr: context.getSourceCode().getText(node.left),
                  enclosingContext: enclosingContext || "global scope"
                },
              });
            }

            // Detect loose equality
            if (node.operator === '==') {
              const enclosingContext = getEnclosingContext(node);
              context.report({
                node,
                messageId: 'looseEquality',
                data: {
                  left: context.getSourceCode().getText(node.left),
                  right: context.getSourceCode().getText(node.right),
                  enclosingContext: enclosingContext || "global scope"
                },
              });
            }
          },

          UnaryExpression(node) {
            // Detect +value or !!value
            if (node.operator === '+' || node.operator === '!' && node.argument.type === 'UnaryExpression') {
              const enclosingContext = getEnclosingContext(node);
              context.report({
                node,
                messageId: 'unaryCoercion',
                data: {
                  op: node.operator,
                  value: context.getSourceCode().getText(node.argument),
                  enclosingContext: enclosingContext || "global scope"
                },
              });
            }
          },

          IfStatement(node) {
            const test = node.test;
            // Detect truthy/falsy coercion in conditionals
            const suspiciousTypes = ['Literal', 'ArrayExpression', 'ObjectExpression'];
            if (suspiciousTypes.includes(test.type)) {
              const enclosingContext = getEnclosingContext(node);
              context.report({
                node: test,
                messageId: 'conditionalCoercion',
                data: {
                  test: context.getSourceCode().getText(test),
                  enclosingContext: enclosingContext || "global scope"
                },
              });
            }
          }
        };
      }
    }
  }
}
