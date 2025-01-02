import react from "eslint-plugin-react";
import typescriptEslint from "@typescript-eslint/eslint-plugin";
import prettier from "eslint-plugin-prettier";
import jsdoc from "eslint-plugin-jsdoc";
import tsParser from "@typescript-eslint/parser";
import _import from "eslint-plugin-import";
import reactHooks from "eslint-plugin-react-hooks";
import unusedImports from "eslint-plugin-unused-imports";
import simpleImportSort from "eslint-plugin-simple-import-sort";
import { fixupPluginRules } from "@eslint/compat";

export default [
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
      react,
      "@typescript-eslint": typescriptEslint,
      "react-hooks": reactHooks,
      "unused-imports": unusedImports,
      "simple-import-sort": simpleImportSort,
      jsdoc,
      import: fixupPluginRules(_import),
      prettier,
    },
    rules: {
      "react-hooks/rules-of-hooks": "error",
      "jsdoc/require-description": "warn",
      "import/no-duplicates": "error",
      "react-hooks/exhaustive-deps": "warn",
      "unused-imports/no-unused-imports": "error",
      "simple-import-sort/imports": "error",
      "simple-import-sort/exports": "error",
      "prettier/prettier": "error",
      "@typescript-eslint/no-explicit-any": "error",
    },
  },
];
