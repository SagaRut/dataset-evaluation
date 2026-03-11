import { getEnclosingContext } from './utils.js';
// TODO cover more cases where object property access affects the control flow
export default {
  rules: {
    "find-object-property-access": {
      meta: {
        type: "problem",
        docs: {
          description: "Detect object property access from function parameters",
        },
        schema: [],
        messages: {
          found: "Object property access found in '{{ enclosingContext }}'.",
        },
      },
      create(context) {
        function checkForObjectPropertyAccess(node, paramName, functionNode) {
          // Look for MemberExpression like foo.bar
          if (node.type === "MemberExpression" && node.object.name === paramName) {
            const enclosingContext = getEnclosingContext(functionNode);
            context.report({
              node,
              messageId: "found",
              data: { enclosingContext: enclosingContext || "global scope" },
            });
          }
        }

        return {
          // Handle function declarations
          FunctionDeclaration(node) {
            node.params.forEach(param => {
              if (param.type === 'Identifier') {
                // Traverse the body of the function to find member expressions in control flow statements
                const body = node.body.body; // Access the function body statements
                body.forEach(statement => {
                  // Handling 'if' statements and their branches
                  if (statement.type === "IfStatement" && statement.test) {
                    if (statement.test.type === "MemberExpression") {
                      checkForObjectPropertyAccess(statement.test, param.name, node);
                    }
                    if (statement.consequent.body) {
                      statement.consequent.body.forEach(consequentStatement => {
                        if (consequentStatement.type === "ExpressionStatement" &&
                          consequentStatement.expression &&
                          consequentStatement.expression.type === "MemberExpression") {
                          checkForObjectPropertyAccess(consequentStatement.expression, param.name, node);
                        }
                      });
                    }
                    if (statement.alternate && statement.alternate.body) {
                      statement.alternate.body.forEach(elseStatement => {
                        if (elseStatement.type === "ExpressionStatement" &&
                          elseStatement.expression &&
                          elseStatement.expression.type === "MemberExpression") {
                          checkForObjectPropertyAccess(elseStatement.expression, param.name, node);
                        }
                      });
                    }
                  }

                  // Handling 'while' loops
                  if (statement.type === "WhileStatement" && statement.test) {
                    if (statement.test.type === "MemberExpression") {
                      checkForObjectPropertyAccess(statement.test, param.name, node);
                    }
                    if (statement.body.body) {
                      statement.body.body.forEach(whileBodyStatement => {
                        if (whileBodyStatement.type === "ExpressionStatement" &&
                          whileBodyStatement.expression &&
                          whileBodyStatement.expression.type === "MemberExpression") {
                          checkForObjectPropertyAccess(whileBodyStatement.expression, param.name, node);
                        }
                      });
                    }
                  }

                  // Handling 'for' loops
                  if (statement.type === "ForStatement") {
                    if (statement.test && statement.test.type === "MemberExpression") {
                      checkForObjectPropertyAccess(statement.test, param.name, node);
                    }
                    if (statement.body.body) {
                      statement.body.body.forEach(forBodyStatement => {
                        if (forBodyStatement.type === "ExpressionStatement" &&
                          forBodyStatement.expression &&
                          forBodyStatement.expression.type === "MemberExpression") {
                          checkForObjectPropertyAccess(forBodyStatement.expression, param.name, node);
                        }
                      });
                    }
                  }

                  // Handling 'for...in' loops specifically
                  if (statement.type === "ForInStatement") {
                    if (statement.right && statement.right.type === "MemberExpression") {
                      checkForObjectPropertyAccess(statement.right, param.name, node);
                    }
                    if (statement.body.body) {
                      statement.body.body.forEach(forInBodyStatement => {
                        if (forInBodyStatement.type === "ExpressionStatement" &&
                          forInBodyStatement.expression &&
                          forInBodyStatement.expression.type === "MemberExpression") {
                          checkForObjectPropertyAccess(forInBodyStatement.expression, param.name, node);
                        }
                      });
                    }
                  }

                  // Handling 'switch' statements
                  if (statement.type === "SwitchStatement") {
                    // Check for member expressions in the 'switch' discriminant (the expression being evaluated)
                    if (statement.discriminant && statement.discriminant.type === "MemberExpression") {
                      checkForObjectPropertyAccess(statement.discriminant, param.name, node);
                    }

                    // Check each case in the switch statement
                    statement.cases.forEach(caseClause => {
                      // Check for member expressions in the 'case' test expression
                      if (caseClause.test && caseClause.test.type === "MemberExpression") {
                        checkForObjectPropertyAccess(caseClause.test, param.name, node);
                      }

                      // Check for member expressions in the body of each case
                      caseClause.consequent.forEach(caseStatement => {
                        if (caseStatement.type === "ExpressionStatement" &&
                          caseStatement.expression &&
                          caseStatement.expression.type === "MemberExpression") {
                          checkForObjectPropertyAccess(caseStatement.expression, param.name, node);
                        }
                      });
                    });
                  }
                });
              }
            });
          },

          // Handle function expressions
          FunctionExpression(node) {
            node.params.forEach(param => {
              if (param.type === 'Identifier') {
                // Traverse the body of the function to find member expressions
                context.getSourceCode().ast.body.forEach(statement => {
                  if (statement.type === "ExpressionStatement" && statement.expression.type === "MemberExpression") {
                    checkForObjectPropertyAccess(statement.expression, param.name, node);
                  }
                });
              }
            });
          },

          // Handle arrow function expressions
          ArrowFunctionExpression(node) {
            node.params.forEach(param => {
              if (param.type === 'Identifier') {
                // Traverse the body of the function to find member expressions
                context.getSourceCode().ast.body.forEach(statement => {
                  if (statement.type === "ExpressionStatement" && statement.expression.type === "MemberExpression") {
                    checkForObjectPropertyAccess(statement.expression, param.name, node);
                  }
                });
              }
            });
          },

          // Handle method definitions
          MethodDefinition(node) {
            node.value.params.forEach(param => {
              if (param.type === 'Identifier') {
                // Traverse the body of the method to find member expressions
                context.getSourceCode().ast.body.forEach(statement => {
                  if (statement.type === "ExpressionStatement" && statement.expression.type === "MemberExpression") {
                    checkForObjectPropertyAccess(statement.expression, param.name, node);
                  }
                });
              }
            });
          },
        };
      },
    },
  },
};
