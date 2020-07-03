import ts from "typescript";
import prettier from "prettier";
import { writeFile } from "fs";
import { getCompilerOptions } from "./getCompilerOptions";

export interface TypeScriptContext {
  program: ts.Program;
  typeChecker: ts.TypeChecker;
  print: (path: string, sourceFile: ts.SourceFile) => Promise<void>;
  sourceFiles: readonly ts.SourceFile[];
  compilerOptions: ts.CompilerOptions;
  printFile: (path: string, contents: string) => Promise<void>;
}

export function typeScriptContext(): TypeScriptContext {
  const opt = getCompilerOptions();

  if (!opt || !opt.fileNames || !opt.options) {
    console.error('Cannot parse tsconfig.json.');
    process.exit(1);
  }

  const program = ts.createProgram(opt.fileNames, opt.options);
  const printer = ts.createPrinter({}, {});

  function printFile(path: string, contents: string) {
    return new Promise<void>((resolve, reject) => {
      writeFile(path, contents, {}, (err) => err ? reject() : resolve());
    });
  }

  return {
    compilerOptions: opt.options,
    program,
    typeChecker: program.getTypeChecker(),
    sourceFiles: program.getSourceFiles(),
    printFile,
    async print(path, sourceFile) {
      const file = prettier.format(
        printer.printFile(sourceFile),
        { parser: "typescript" },
      );
      await printFile(path, file);     
    },
  }
}
