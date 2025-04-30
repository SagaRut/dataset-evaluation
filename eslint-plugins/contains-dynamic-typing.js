import { getEnclosingContext } from './utils.js';
export default {
    rules: {
        "find-dynamic-typing": {
            meta: {
                type: "problem",
                docs: {
                    description: "find usage of dynamic typing(let, var, const)",
                },
                schema: [],
                messages: {
                    found: "Usage of '{{ kind }}' found in '{{ enclosingContext }}'.",
                },
            },
            create(context) {
                return {
                    VariableDeclaration(node) {
                        if (node.kind === "let" || node.kind === "var" || node.kind === "const") {
                            const enclosingContext = getEnclosingContext(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { kind: node.kind, enclosingContext: enclosingContext || "global scope" },
                            });
                        }
                    },
                };
            },
        },
    },
};
