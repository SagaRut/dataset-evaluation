/**
 * Helper function to get all enclosing named context
 */
export function getEnclosingContext(node) {
    const context = [];
    let current = node;

    while (current) {
        if (
            current.type === "FunctionDeclaration" ||
            current.type === "FunctionExpression" ||
            current.type === "ArrowFunctionExpression"
        ) {
            if (current.id && current.id.name) {
                context.push(`function '${current.id.name}'`);
            } else if (current.parent && current.parent.type === "VariableDeclarator") {
                // Arrow function assigned to a variable
                const varName = current.parent.id.name;
                context.push(`variable '${varName}' arrow function`);
            } else {
                context.push("anonymous function");
            }
        } else if (current.type === "ClassDeclaration") {
            if (current.id && current.id.name) {
                context.push(`class '${current.id.name}'`);
            } else {
                context.push("anonymous class");
            }
        } else if (current.type === "MethodDefinition") {
            if (current.key && current.key.name) {
                context.push(`method '${current.key.name}'`);
            }
        } else if (
            current.type === "AssignmentExpression" &&
            current.left.type === "MemberExpression" &&
            current.left.object &&
            current.left.object.type === "Identifier" &&
            current.left.property &&
            current.left.property.type === "Identifier"
        ) {
            context.push(`object '${current.left.object.name}' property '${current.left.property.name}'`);
        }
        current = current.parent;
    }

    return context.reverse().join(" > ");
}
