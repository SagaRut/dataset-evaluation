import { getEnclosingContext } from './utils.js';

export default {
  rules: {
    "find-dynamic-object-manipulation": {
      meta: {
        type: "problem",
        docs: {
          description: "Detect dynamic object and property manipulation at runtime.",
        },
        schema: [],
        messages: {
          dynamicAccess: "Dynamic property '{{ prop }}' manipulated in {{ enclosingContext }}.",
        },
      },
      create(context) {
        return {
          // Case 1: obj[key] = value
          AssignmentExpression(node) {
            const { left } = node;
            if (
              left.type === 'MemberExpression' &&
              left.computed &&
              left.property.type !== 'Literal' // if property is not a known static string/number
            ) {
              const enclosingContext = getEnclosingContext(node);
              context.report({
                node: left.property,
                messageId: 'dynamicAccess',
                data: {
                  prop: '[computed]',
                  enclosingContext: enclosingContext || 'global scope',
                },
              });
            }
          },

          // Case 2: delete obj[key]
          UnaryExpression(node) {
            if (
              node.operator === 'delete' &&
              node.argument.type === 'MemberExpression' &&
              node.argument.computed
            ) {
              const enclosingContext = getEnclosingContext(node);
              context.report({
                node: node.argument.property,
                messageId: 'dynamicAccess',
                data: {
                  prop: '[computed]',
                  enclosingContext: enclosingContext || 'global scope',
                },
              });
            }
          },

          // Case 3: Object.defineProperty
          CallExpression(node) {
            if (
              node.callee.type === 'MemberExpression' &&
              node.callee.object.name === 'Object' &&
              node.callee.property.name === 'defineProperty'
            ) {
              const enclosingContext = getEnclosingContext(node);
              context.report({
                node: node.callee.property,
                messageId: 'dynamicAccess',
                data: {
                  prop: 'defineProperty',
                  enclosingContext: enclosingContext || 'global scope',
                },
              });
            }

            // Case 4: Object.assign
            if (
              node.callee.type === 'MemberExpression' &&
              node.callee.object.name === 'Object' &&
              node.callee.property.name === 'assign'
            ) {
              const enclosingContext = getEnclosingContext(node);
              context.report({
                node: node.callee.property,
                messageId: 'dynamicAccess',
                data: {
                  prop: 'assign',
                  enclosingContext: enclosingContext || 'global scope',
                },
              });
            }
          }
        };
      }
    }
  }
};
