import { getEnclosingContext } from './utils.js';
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
                    found: "Asynchronous behaviour found in '{{ enclosingContext }}'.",
                },
            },
            create(context) {
                return {
                    // Detect usage of the Promise constructor
                    // Example: const p = new Promise((resolve, reject) => {});
                    Identifier(node) {
                        if (node.name === "Promise") {
                            const enclosingContext = getEnclosingContext(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { enclosingContext: enclosingContext || "global scope" },
                            });
                        }
                    },
                    // Detect async function declarations
                    // Example: async function fetchData() { ... }
                    FunctionDeclaration(node) {
                        if (node.async) {
                            const enclosingContext = getEnclosingContext(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { enclosingContext: enclosingContext || "global scope" },
                            });
                        }
                    },
                    // Detect async function expressions
                    // Example: const fn = async function() { ... };
                    FunctionExpression(node) {
                        if (node.async) {
                            const enclosingContext = getEnclosingContext(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { enclosingContext: enclosingContext || "global scope" },
                            });
                        }
                    },
                    // Detect async arrow functions
                    // Example: const load = async () => { ... };
                    ArrowFunctionExpression(node) {
                        if (node.async) {
                            const enclosingContext = getEnclosingContext(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { enclosingContext: enclosingContext || "global scope" },
                            });
                        }
                    },
                    // Detect usage of await expressions
                    // Example: await fetch(url);
                    AwaitExpression(node) {
                        const enclosingContext = getEnclosingContext(node);
                        context.report({
                            node,
                            messageId: "found",
                            data: { enclosingContext: enclosingContext || "global scope" },
                        });
                    },
                };
            },
        },
    },
};
