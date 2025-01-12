export default {
    rules: {
        "LOC": {
            meta: {
                type: "problem",
                docs: {
                    description: "Report the number of lines of code in a function",
                },
                schema: [],
                messages: {
                    loc: "Unit '{{ name }}' has {{ loc }} lines of code.",
                },
            },
            create(context) {
                return {
                    // For functions
                    FunctionDeclaration(node) {
                        const loc = node.loc.end.line - node.loc.start.line + 1;
                        const functionName = node.id ? node.id.name : "anonymous";
                        context.report({
                            node,
                            messageId: "loc",
                            data: { name: functionName, loc },
                        });
                    },
                    // For classes
                    ClassDeclaration(node) {
                        const loc = node.loc.end.line - node.loc.start.line + 1;
                        const className = node.id ? node.id.name : "anonymous";
                        context.report({
                            node,
                            messageId: "loc",
                            data: { name: className, loc },
                        });
                    },
                };
            },
        },
    },
};
