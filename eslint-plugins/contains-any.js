import { getEnclosingContexts } from './utils.js';

export default {
    rules: {
        'find-any-usage': {
            meta: {
                type: 'problem',
                docs: {
                    description: 'Detect usage of `any` as a type in TypeScript code',
                },
                schema: [],
                messages: {
                    found: "Usage of the 'any' type found in '{{ contexts }}'.",
                },
            },
            create(context) {
                return {
                    // Look for function declarations with 'any' type
                    'FunctionDeclaration[params.typeAnnotation.type="TSTypeAnnotation"][params.typeAnnotation.typeAnnotation.type="TSAnyKeyword"]': (node) => {
                        const contexts = getEnclosingContexts(node);
                        context.report({
                            node,
                            messageId: 'found',
                            data: { kind: node.kind, contexts: contexts || "global scope" },
                        });
                    },

                    // Look for arrow function expressions with 'any' type
                    'ArrowFunctionExpression[params.typeAnnotation.type="TSTypeAnnotation"][params.typeAnnotation.typeAnnotation.type="TSAnyKeyword"]': (node) => {
                        const contexts = getEnclosingContexts(node);
                        const paramNames = node.params.map(param => param.name).join(', ');
                        context.report({
                            node,
                            messageId: 'found',
                            data: { location: `arrow function(${paramNames}) > ${contexts}` },
                        });
                    },

                    // Look for method declarations with 'any' type
                    'MethodDefinition[params.typeAnnotation.type="TSTypeAnnotation"][params.typeAnnotation.typeAnnotation.type="TSAnyKeyword"]': (node) => {
                        const contexts = getEnclosingContexts(node);
                        const methodName = node.key.type === 'Identifier' ? node.key.name : 'anonymous method';
                        context.report({
                            node,
                            messageId: 'found',
                            data: { location: `method ${methodName} > ${contexts}` },
                        });
                    },

                    // Look for variable declarations with 'any' type
                    'VariableDeclaration[declarations.typeAnnotation.type="TSTypeAnnotation"][declarations.typeAnnotation.typeAnnotation.type="TSAnyKeyword"]': (node) => {
                        const contexts = getEnclosingContexts(node);
                        const variableName = node.declarations[0].id.name;
                        context.report({
                            node,
                            messageId: 'found',
                            data: { location: `variable ${variableName} > ${contexts}` },
                        });
                    },
                };
            },
        },
    },
};
