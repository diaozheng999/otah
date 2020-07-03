// @barrel export OtahConfig

interface OtahDenoModuleLookupResponse {
  source: string;
  types: string;
}

export interface OtahConfig {
  denoModuleLookup: (module: string) => string | OtahDenoModuleLookupResponse;
  denoOut: string;
  root: string;
}

export function getOtahConfig(): OtahConfig {
  const config = require(process.cwd() + "/.otahconfig");
  return config;
}
