// @barrel ignore
import { deno } from "../rewriter";
import { typeScriptContext, getOtahConfig, Command } from "../utils";
import path from "path";
import ts from "typescript";

export default class Deno extends Command {
  async run() {
    const config = getOtahConfig();
    const {
      program,
      typeChecker,
      print,
      sourceFiles,
      compilerOptions: options,
    } = typeScriptContext();

    const promises: Promise<void>[] = [];

    for (const sourceFile of sourceFiles) {
      if (
        program.isSourceFileFromExternalLibrary(sourceFile) ||
        program.isSourceFileDefaultLibrary(sourceFile)
      ) {
        continue;
      }

      const fileName = path.resolve(sourceFile.fileName);

      this.log(`Rewriting ${fileName}...`);

      const resolver = deno.makeResolver({
        typeChecker,
        file: sourceFile,
        options,
        config,
        cmd: this,
      });
      
      const result = ts.transform(sourceFile, [resolver.transform]);

      promises.push(print(resolver.denoFile, result.transformed[0]));
    }
    await Promise.all(promises);
  }
}
