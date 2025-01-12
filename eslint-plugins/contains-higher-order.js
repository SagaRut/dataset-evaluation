import { getEnclosingContexts } from "./utils.js";
// TODO Fix this does not find function arguments in highest level, also not return functions
export default {
  rules: {
    "find-higher-order": {
      meta: {
        type: "problem",
        docs: {
          description: "Find higher-order functions",
        },
        schema: [],
        messages: {
          found: "Higher-order function detected in '{{ contexts }}'.",
        },
      },
      create(context) {
        function reportHigherOrderFunction(node) {
          const contexts = getEnclosingContexts(node);
          context.report({
            node,
            messageId: "found",
            data: { contexts: contexts || "global scope" },
          });
        }

        function isFunctionType(param) {
          return (
            param.type === "Identifier" &&
            param.typeAnnotation &&
            param.typeAnnotation.typeAnnotation.type === "FunctionTypeAnnotation"
          );
        }

        function hasFunctionParameter(node) {
          if (
            node.params &&
            node.params.some(
              (param) =>
                param.type === "Identifier" &&
                (param.typeAnnotation?.type === "TSTypeAnnotation" &&
                  param.typeAnnotation.typeAnnotation.type === "TSFunctionType")
            )
          )
          {
            return true;}
          else{return false;}
        }

        function isHigherOrderFunctionArgument(node) {
          return (
            node.arguments &&
            node.arguments.some(
              (arg) =>
                arg.type === "FunctionExpression" ||
                arg.type === "ArrowFunctionExpression"
            )
          );
        }

        function isHigherOrderFunctionReturn(node) {
          return (
            node.body.type === "BlockStatement" &&
            node.body.body.some(
              (statement) =>
                statement.type === "ReturnStatement" &&
                (statement.argument?.type === "FunctionExpression" ||
                  statement.argument?.type === "ArrowFunctionExpression")
            )
          );
        }

        return {
          CallExpression(node) {
            if (isHigherOrderFunctionArgument(node)) {
              reportHigherOrderFunction(node);
            }
          },
          FunctionDeclaration(node) {
            if (hasFunctionParameter(node) || isHigherOrderFunctionReturn(node)) {
              reportHigherOrderFunction(node);
            }
          },
          FunctionExpression(node) {
            if (hasFunctionParameter(node) || isHigherOrderFunctionReturn(node)) {
              reportHigherOrderFunction(node);
            }
          },
          ArrowFunctionExpression(node) {
            if (
              node.body.type === "FunctionExpression" ||
              node.body.type === "ArrowFunctionExpression"
            ) {
              reportHigherOrderFunction(node);
            }
          },
        };
      },
    },
  },
};
