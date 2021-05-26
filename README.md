# otah

Selective bundling script for React Native.

## Installation

`npm install --save-dev otah`

## Commands

The following commands are supported:
1. `otah barrel` - a barrelling tool
2. `otah clean` - remove barrelled (`index.ts`) artefacts
3. `otah bundle` - a wrapper around React Native bundler to produce a specific targetted bundle for each platform.

**note** `otah bundle` does not support generating Hermes bundles for iOS yet.


### `otah barrel`

Walks through recursively and produce an `index.ts` file for each directory. This allows the use of:

```typescript
import { Component1, Component2 } from "dir";
```

instead of

```typescript
import { Component1 } from "dir/Component1";
import { Component2 } from "dir/Component2";
```

By default, for each `FileName.ts{x}`, the following line will be generated in `index.ts`:

```typescript
import { FileName } from "./FileName";
export { FileName };
```

There are, however, some ways of customising this behaviour:

#### `@barrel ignore`

Adding `@barrel ignore` as a comment in the file will result in the barreller ignoring this file.

#### `@barrel export all`

Adding `@barrel export all` as a comment in the file will result in the following behaviour:

```typescript
import * as FileName from "./FileName";
export { FileName };
```

essentially allowing exporting an entire module as a named entity.

#### `@barrel export <item1>, <item2>`

Adding `@barrel export item1, item2, ...` as a comment in the file will result in:
```typescript
import { FileName, item1, item2 } from "./FileName;
export { FileName, item1, item2 };
```

This is used to expose other items in addition to the base export.

This can also be used in conjunction with `@barrel export all`.

#### `@barrel component type`

Adding `@barrel component type` as a comment will result in the following being exported:
```typescript
import { FileName, FileNameProps } from "./FileName";
export { FileName, FileNameProps };
```

We recommend defining the props explicitly as an interface for each React component, for maintainability and easy reference.

This allows a consistent way of refering to the prop types. We provide both the `eslint`-style `FileNameProps` interface definition, and the old `tslint`-style `IFileNameProps` interface definition.

#### `@barrel hook`

Adding `@barrel hook` will expose a React hook-style export based on a file, so:

```typescript
import { useFileName } from "./FileName";
export { useFileName }
```

Be sure to name your files accordingly.

#### `@barrel ignore`

Adding `@barrel ignore` as a comment will result in the file being skipped for barrelling.


