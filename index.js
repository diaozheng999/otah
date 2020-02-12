// This file exists because we need to import (and assign) everything before
// importing all other stuff. However, babel hoists all exports to the top
// before any declarations.

if (typeof __OTAH_DISTRIBUTION_MODE__ !== "string") {
  global.__OTAH_DISTRIBUTION_MODE__ = "APPLE";
}

if (typeof __OTAH_ENV__ !== "string") {
  global.__OTAH_ENV__ = "STAGING";
}
