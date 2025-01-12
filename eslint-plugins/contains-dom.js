import { getEnclosingContexts } from './utils.js';

export default {
  rules: {
    "find-dom-interaction": {
      meta: {
        type: "problem",
        docs: {
          description: "find usage of dom interaction",
        },
        schema: [],
        messages: {
          found: "Usage of dom interaction found in '{{ contexts }}'.",
        },
      },
      create(context) {
        return {
          // Check for DOM interactions in function calls
          CallExpression(node) {
            const callee = node.callee;
            if (callee.type === 'MemberExpression') {
              const object = callee.object;
              const property = callee.property;

              // Check for interactions with document or window
              if (object.name === "document" || object.name === "window") {
                if (["getElementById", "querySelector", "querySelectorAll", "createElement", "appendChild", "removeChild"].includes(property.name)) {
                  const contexts = getEnclosingContexts(node);
                  context.report({
                    node,
                    messageId: "found",
                    data: { contexts: contexts || "global scope" },
                  });
                }
              }

              // Check for element interactions (methods directly on DOM elements)
              else if (object.type === 'Identifier') {
                if (["addEventListener", "removeEventListener", "setAttribute", "classList.add", "classList.remove"].includes(property.name)) {
                  const contexts = getEnclosingContexts(node);
                  context.report({
                    node,
                    messageId: "found",
                    data: { contexts: contexts || "global scope" },
                  });
                }
              }
            }
          },
        };
      },
    },
  },
};
