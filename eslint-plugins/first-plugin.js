export default {
    rules: {
        "max-params": {
            meta: {
                type: "suggestion",
                docs: {
                    description: "enforce a maximum number of parameters in function definitions",
                },
                schema: [
                    {
                        type: "integer",
                        minimum: 0,
                    },
                ],
            },
            create(context) {
                const maxParams = context.options[0] || 5; // Default to 5
                return {
                    FunctionDeclaration(node) {
                        if (node.params.length > maxParams) {
                            context.report({
                                node,
                                message: `Function has too many parameters ({{count}}). Maximum allowed is {{max}}.`,
                                data: {
                                    count: node.params.length,
                                    max: maxParams,
                                },
                            });
                        }
                    },
                };
            },
        },
    },
};
