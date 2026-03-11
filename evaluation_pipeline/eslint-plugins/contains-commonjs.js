import { getEnclosingContext } from './utils.js';

export default {
    rules: {
        "find-commonjs": {
            meta: {
                type: "problem",
                docs: {
                    description: "Detect usage of CommonJS code (require, module.exports, exports).",
                },
                schema: [],
                messages: {
                    found: "CommonJS usage '{{ type }}' found in '{{ enclosingContext }}'.",
                },
            },
            create(context) {
                return {
                    CallExpression(node) {
                        // Detect `require`
                        if (
                            node.callee.type === "Identifier" &&
                            node.callee.name === "require"
                        ) {
                            const enclosingContext = getEnclosingContext(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { type: "require", enclosingContext: enclosingContext || "global scope" },
                            });
                        }
                    },
                    MemberExpression(node) {
                        // Detect `module.exports`
                        if (
                            node.object.type === "Identifier" &&
                            node.object.name === "module" &&
                            node.property.type === "Identifier" &&
                            node.property.name === "exports"
                        ) {
                            const enclosingContext = getEnclosingContext(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { type: "module.exports", enclosingContext: enclosingContext || "global scope" },
                            });
                        }

                        // Detect `exports.something`
                        if (
                            node.object.type === "Identifier" &&
                            node.object.name === "exports"
                        ) {
                            const enclosingContext = getEnclosingContext(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { type: "exports", enclosingContext: enclosingContext || "global scope" },
                            });
                        }
                    },
                };
            },
        },
    },
};
