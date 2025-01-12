export default {
    rules: {
        "count-branches": {
            meta: {
                type: "problem",
                docs: {
                    description: "Count the number of branches in a function",
                    recommended: false,
                },
                schema: [],
                messages: {
                    branchCount: "Function '{{ name }}' contains {{ count }} branches.",
                },
            },
            create(context) {
                return {
                    FunctionDeclaration(node) {
                        let branchCount = 0;

                        // Traverse the function's body manually
                        node.body.body.forEach((statement) => {
                            if (statement.type === "IfStatement") {
                                branchCount++;
                                if (statement.alternate) branchCount++;
                            } else if (statement.type === "SwitchStatement") {
                                branchCount += statement.cases.length;
                            } else if (statement.type === "ConditionalExpression") {
                                branchCount += 2; // Ternary operator
                            }
                        });

                        context.report({
                            node,
                            messageId: "branchCount",
                            data: { name: node.id.name, count: branchCount },
                        });
                    },
                };
            },
        },
    },
};
