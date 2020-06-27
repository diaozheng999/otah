import ts from "typescript";
import { getCompilerOptions } from "../utils";
import path from "path";

function __readPackageJSON() {
  const f = require(process.cwd() + '/package.json');
  return f;
}

interface ResolverConfig {
  typeChecker: ts.TypeChecker;
  file: ts.SourceFile;
  options: ts.CompilerOptions;
}

function makeResolver( {typeChecker, file, options}: ResolverConfig) {
  const currentPath = path.dirname(file.fileName);

  const nodeModules = path.resolve('node_modules');

  return {
    resolve(absoluteFileName: string) {
      const relativePath: string = path
        .relative(currentPath, absoluteFileName)
        .replace(/\\/g, '/');
      
      if (!relativePath.includes('/')) {
        return `./${relativePath}`;
      }
      return relativePath;
    },
    resolveImport(node: ts.ImportDeclaration) {
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

          

          console.log(`read module name: ${moduleName}`);

          if (!resolved.resolvedModule) {
            console.error('Unable to resolve module');
          }

          const absoluteFileName = path.resolve(decl.fileName);

          if (!path.relative(nodeModules, absoluteFileName).startsWith('..')) {
            console.warn(node.moduleSpecifier.getText());

          } else {
            console.warn(this.resolve(absoluteFileName));
          }

        }
      }
    }
  }
}

function compile(fileNames: string[], options: ts.CompilerOptions): void {

  const program = ts.createProgram(fileNames, options);
  const typeChecker = program.getTypeChecker();


  const sourceFiles = program.getSourceFiles();
  for (const sourceFile of sourceFiles) {
    if (
      program.isSourceFileFromExternalLibrary(sourceFile) ||
      program.isSourceFileDefaultLibrary(sourceFile)
    ) {
      continue;
    }

    const fileName = path.resolve(sourceFile.fileName);

    const resolver = makeResolver({ typeChecker, file: sourceFile, options });

    console.warn(`===\n${fileName}\n===`);
    

    sourceFile.forEachChild((node) => {
      if (ts.isImportDeclaration(node)) {
        resolver.resolveImport(node);
      }
    });
    
    

  }
}

const opt = getCompilerOptions();

compile(opt?.fileNames!, opt?.options!);


export const deno = compile;