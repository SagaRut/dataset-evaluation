import { getEnclosingContexts } from './utils.js';
export default {
    rules: {
        "find-async": {
            meta: {
                type: "problem",
                docs: {
                    description: "find asynchronous behaviour",
                },
                schema: [],
                messages: {
                    found: "Asynchronous behaviour found in '{{ contexts }}'.",
                },
            },
            create(context) {
                return {
                    Identifier(node) {
                        if (node.name === "Promise") {
                            const contexts = getEnclosingContexts(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { contexts: contexts || "global scope" },
                            });
                        }
                    },
                    FunctionDeclaration(node) {
                        if (node.async) {
                            const contexts = getEnclosingContexts(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { contexts: contexts || "global scope" },
                            });
                        }
                    },
                    FunctionExpression(node) {
                        if (node.async) {
                            const contexts = getEnclosingContexts(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { contexts: contexts || "global scope" },
                            });
                        }
                    },
                    ArrowFunctionExpression(node) {
                        if (node.async) {
                            const contexts = getEnclosingContexts(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { contexts: contexts || "global scope" },
                            });
                        }
                    },
                    AwaitExpression(node) {
                        const contexts = getEnclosingContexts(node);
                        context.report({
                            node,
                            messageId: "found",
                            data: { contexts: contexts || "global scope" },
                        });
                    },
                };
            },
        },
    },
};
