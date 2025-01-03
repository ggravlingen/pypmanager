import typescriptEslint from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";
import { type Linter } from "eslint";
import importPlugin from "eslint-plugin-import";
import jsdoc from "eslint-plugin-jsdoc";
import prettier from "eslint-plugin-prettier";
import pluginReact from "eslint-plugin-react";
import pluginHooks from "eslint-plugin-react-hooks";
import simpleImportSort from "eslint-plugin-simple-import-sort";
import unusedImports from "eslint-plugin-unused-imports";

const config: Linter.Config[] = [
  {
    name: "frontend",
    files: ["**/*.ts", "**/*.tsx"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      parser: tsParser,
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    settings: {
      react: {
        version: "detect",
      },
    },
    plugins: {
      pluginReact,
      "@typescript-eslint": typescriptEslint,
      "react-hooks": pluginHooks,
      "unused-imports": unusedImports,
      "simple-import-sort": simpleImportSort,
      jsdoc,
      import: importPlugin,
      prettier,
    },
    rules: {
      ...pluginHooks.configs.recommended.rules,

      // warn
      "jsdoc/require-description": "warn",
      "no-console": "warn",

      // error
      "@typescript-eslint/consistent-type-imports": "error",
      "@typescript-eslint/no-explicit-any": "error",
      "import/no-duplicates": "error",
      "prettier/prettier": "error",
      "simple-import-sort/exports": "error",
      "simple-import-sort/imports": "error",
      "unused-imports/no-unused-imports": "error",
    },
  },
];

export default config;
