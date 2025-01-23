import { getEnclosingContexts } from './utils.js';

export default {
    rules: {
        "find-closures": {
            meta: {
                type: "problem",
                docs: {
                    description: "Detect usage of closures in JavaScript code.",
                },
                schema: [],
                messages: {
                    found: "Closure detected in '{{ contexts }}'.",
                },
            },
            create(context) {
                return {
                    FunctionExpression(node) {
                        if (node.parent && node.parent.type === "CallExpression") {
                            const contexts = getEnclosingContexts(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { contexts: contexts || "global scope" },
                            });
                        }
                    },
                    ArrowFunctionExpression(node) {
                        if (node.parent && node.parent.type === "CallExpression") {
                            const contexts = getEnclosingContexts(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { contexts: contexts || "global scope" },
                            });
                        }
                    },
                };
            },
        },
    },
};
