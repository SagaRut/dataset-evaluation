import { getEnclosingContext } from './utils.js';

export default {
    rules: {
        "find-prototype": {
            meta: {
                type: "problem",
                docs: {
                    description: "Detect usage of prototype access, creation, or mutation in JavaScript code.",
                },
                schema: [],
                messages: {
                    found: "Prototype usage detected in '{{ enclosingContext }}'.",
                },
            },
            create(context) {
                return {
                    MemberExpression(node) {
                        // Detect direct prototype access (e.g., Object.prototype, Array.prototype)
                        if (
                            node.object &&
                            node.object.type === "Identifier" &&
                            node.property &&
                            node.property.name === "prototype"
                        ) {
                            const enclosingContext = getEnclosingContext(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { enclosingContext: enclosingContext || "global scope" },
                            });
                        }
                    },
                    CallExpression(node) {
                        // Detect Object.create calls
                        if (
                            node.callee.type === "MemberExpression" &&
                            node.callee.object.name === "Object" &&
                            node.callee.property.name === "create"
                        ) {
                            const enclosingContext = getEnclosingContext(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { enclosingContext: enclosingContext || "global scope" },
                            });
                        }
                    },
                    AssignmentExpression(node) {
                        // Detect assignments to prototype properties (e.g., MyClass.prototype.someMethod = ...)
                        if (
                            node.left.type === "MemberExpression" &&
                            node.left.object.type === "MemberExpression" &&
                            node.left.object.property &&
                            node.left.object.property.name === "prototype"
                        ) {
                            const enclosingContext = getEnclosingContext(node);
                            context.report({
                                node,
                                messageId: "found",
                                data: { enclosingContext: enclosingContext || "global scope" },
                            });
                        }
                    },
                };
            },
        },
    },
};
