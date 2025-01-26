/**
 * Helper function to get all enclosing named contexts
 */
export function getEnclosingContexts(node) {
    const contexts = [];
    let current = node;

    while (current) {
        if (
            current.type === "FunctionDeclaration" ||
            current.type === "FunctionExpression" ||
            current.type === "ArrowFunctionExpression"
        ) {
            if (current.id && current.id.name) {
                contexts.push(`function '${current.id.name}'`);
            } else if (current.parent && current.parent.type === "VariableDeclarator") {
                // Arrow function assigned to a variable
                const varName = current.parent.id.name;
                contexts.push(`variable '${varName}' arrow function`);
            } else {
                contexts.push("anonymous function");
            }
        } else if (current.type === "ClassDeclaration") {
            if (current.id && current.id.name) {
                contexts.push(`class '${current.id.name}'`);
            } else {
                contexts.push("anonymous class");
            }
        } else if (current.type === "MethodDefinition") {
            if (current.key && current.key.name) {
                contexts.push(`method '${current.key.name}'`);
            }
        } else if (
            current.type === "AssignmentExpression" &&
            current.left.type === "MemberExpression" &&
            current.left.object &&
            current.left.object.type === "Identifier" &&
            current.left.property &&
            current.left.property.type === "Identifier"
        ) {
            contexts.push(`object '${current.left.object.name}' property '${current.left.property.name}'`);
        }
        current = current.parent;
    }

    return contexts.reverse().join(" > ");
}
