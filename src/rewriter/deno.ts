// @barrel export all

import ts from "typescript";
import { OtahConfig } from "../utils";
import path from "path";
import Command from "@oclif/command";

interface ResolverConfig {
  typeChecker: ts.TypeChecker;
  file: ts.SourceFile;
  options: ts.CompilerOptions;
  config: OtahConfig;
  cmd: Command;
}

export function makeResolver({
  typeChecker,
  file,
  options,
  config,
  cmd,
}: ResolverConfig) {
  const currentPath = path.dirname(file.fileName);

  const currentFile = path.resolve(file.fileName);
  const relative = path.relative(path.resolve(config.root), currentFile);

  const denoFile = path.resolve(config.denoOut + path.sep + relative);

  function resolveImport(node: ts.ImportDeclaration) {
    if (!ts.isStringLiteral(node.moduleSpecifier)) {
      return node;
    }

    const symbol = typeChecker.getSymbolAtLocation(node.moduleSpecifier);

    for (const decl of symbol?.getDeclarations()!) {
      if (ts.isSourceFile(decl)) {
        const moduleName: string = eval(node.moduleSpecifier.getText());

        const resolved = ts.resolveModuleName(
          moduleName,
          file.fileName,
          options,
          {
            fileExists: ts.sys.fileExists,
            readFile: ts.sys.readFile,
            directoryExists: ts.sys.directoryExists,
            getCurrentDirectory: ts.sys.getCurrentDirectory,
            getDirectories: ts.sys.getDirectories,
          }
        );

        if (!resolved.resolvedModule) {
          cmd.error("Unable to resolve module", {
            code: "DENO_UNRESOLVED_MODULE",
          });
        }

        if (resolved.resolvedModule?.isExternalLibraryImport) {
          const lookupResult = config.denoModuleLookup(moduleName);

          if (!lookupResult) {
            cmd.warn(
              new Error(`Cannot determine Deno module for \`${moduleName}\`.`)
            );
            return ts.createImportDeclaration(
              node.decorators,
              node.modifiers,
              node.importClause,
              ts.createStringLiteral(`${moduleName}.ts`)
            );
          }

          const decl = ts.createImportDeclaration(
            node.decorators,
            node.modifiers,
            node.importClause,
            ts.createStringLiteral(
              typeof lookupResult === "string"
                ? lookupResult
                : lookupResult.source
            )
          );

          if (typeof lookupResult !== "string" && lookupResult.types) {
            ts.addSyntheticLeadingComment(
              decl,
              ts.SyntaxKind.SingleLineCommentTrivia,
              ` @deno-types="${lookupResult.types}"`,
              true
            );
          }
          return decl;
        } else {
          return ts.createImportDeclaration(
            node.decorators,
            node.modifiers,
            node.importClause,
            ts.createStringLiteral(`${moduleName}.ts`)
          );
        }
      }
    }
    return node;
  }

  return {
    resolve(absoluteFileName: string) {
      const relativePath: string = path
        .relative(currentPath, absoluteFileName)
        .replace(/\\/g, "/");

      if (!relativePath.includes("/")) {
        return `./${relativePath}`;
      }
      return relativePath;
    },

    resolveImport,

    denoFile,

    transform(context: ts.TransformationContext) {
      return (node: ts.SourceFile) => {
        const transformNode = (node: ts.Node): ts.Node => {
          node = ts.visitEachChild(node, transformNode, context);
          if (ts.isImportDeclaration(node)) {
            return resolveImport(node);
          }
          return node;
        };
        return ts.visitNode(node, transformNode);
      };
    },
  };
}
