import { getEnclosingContext } from './utils.js';

export default {
  rules: {
    "find-implicit-globals": {
      meta: {
        type: "problem",
        docs: {
          description: "Detect implicit global variable assignments.",
        },
        schema: [],
        messages: {
          foundImplicitGlobal: "Implicit global variable found in '{{ enclosingContext }}'.",
        },
      },
      create(context) {
        // A set to track variables declared in the current file scope
        const declaredVariables = new Set();

        // Collect declared variable names from variable declarations (e.g., `var x = 5`)
        function addDeclaredVariables(node) {
          if (node.type === 'VariableDeclaration') {
            for (const decl of node.declarations) {
              if (decl.id.type === 'Identifier') {
                declaredVariables.add(decl.id.name);
              }
            }
          }
        }

        return {
          // Clear the set at the start of linting a program to avoid residue across files
          Program(node) {
            declaredVariables.clear();
          },

          // Track declared variables to distinguish them from implicit globals
          VariableDeclaration: addDeclaredVariables,

          // Check for assignments to identifiers that haven't been declared
          AssignmentExpression(node) {
            if (node.left.type !== 'Identifier') return;

            const name = node.left.name;

            // If the variable wasn't declared, treat it as an implicit global
            if (!declaredVariables.has(name)) {
              const enclosingContext = getEnclosingContext?.(node) || "unknown";
              context.report({
                node,
                messageId: "foundImplicitGlobal",
                data: { enclosingContext },
              });
            }
          },
        };
      }
    }
  }
};