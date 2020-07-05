import ts from "typescript";
import { Command, typeScriptContext } from "../utils";


async function estimate(sourceFile: ts.SourceFile) {
  let nodeCount = 0;
  sourceFile.forEachChild((node) => {
    console.warn(node.kind);
    ++nodeCount;
  });
  return nodeCount;
}


export class Opt extends Command {
  async run() {
    const ctx = typeScriptContext();
    for (const sourceFile of ctx.sourceFiles) {
      if (
        ctx.program.isSourceFileFromExternalLibrary(sourceFile) ||
        ctx.program.isSourceFileDefaultLibrary(sourceFile)
      ) {
        continue;
      }
      this.warn(sourceFile.fileName);
      this.log(`estimate: ${await estimate(sourceFile)}`);
    }
  }
}