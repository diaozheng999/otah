import * as ts from "typescript";



export function getCompilerOptions() {
  const parseConfigHost: ts.ParseConfigHost = {
    fileExists: ts.sys.fileExists,
    readFile: ts.sys.readFile,
    readDirectory: ts.sys.readDirectory,
    useCaseSensitiveFileNames: true,
  }
  
  const configFileName = ts.findConfigFile('.', ts.sys.fileExists);

  if (!configFileName) {
    return;
  }

  const configFile = ts.readConfigFile(configFileName, ts.sys.readFile);

  return ts.parseJsonConfigFileContent(configFile.config, parseConfigHost, '.');
}
