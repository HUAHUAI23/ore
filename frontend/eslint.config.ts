// eslint.config.ts
import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import reactPlugin from "eslint-plugin-react";
import reactHooksPlugin from "eslint-plugin-react-hooks";
import jsxA11yPlugin from "eslint-plugin-jsx-a11y";
import simpleImportSort from "eslint-plugin-simple-import-sort";
import prettierConfig from "eslint-config-prettier";

export default tseslint.config(
  // 基础 JavaScript 推荐配置
  js.configs.recommended,

  // TypeScript 推荐配置
  ...tseslint.configs.recommended,

  // 全局配置
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
      ecmaVersion: "latest",
      sourceType: "module",
    },
  },

  // TypeScript 和 React 文件配置
  {
    files: ["**/*.{ts,tsx,js,jsx}"],
    plugins: {
      react: reactPlugin,
      "react-hooks": reactHooksPlugin,
      "jsx-a11y": jsxA11yPlugin,
      "simple-import-sort": simpleImportSort,
    },
    rules: {
      // React 配置
      ...reactPlugin.configs.recommended.rules,
      ...reactPlugin.configs["jsx-runtime"].rules,
      ...reactHooksPlugin.configs.recommended.rules,
      ...jsxA11yPlugin.configs.recommended.rules,

      // Import 排序配置
      "simple-import-sort/imports": [
        "error",
        {
          groups: [
            // 1. React 相关包优先
            ["^react", "^@?\\w"],
            // 2. 内部模块（@/ 或 components/ 开头）
            ["^(@|components)(/.*|$)"],
            // 3. Side effect imports (import './styles.css')
            ["^\\u0000"],
            // 4. 父级目录的相对导入 '../'
            ["^\\.\\.(?!/?$)", "^\\.\\./?$"],
            // 5. 同级目录的相对导入 './'
            ["^\\./(?=.*/)(?!/?$)", "^\\.(?!/?$)", "^\\./?$"],
            // 6. 样式文件
            ["^.+\\.(css|scss|less|stylus)$"],
          ],
        },
      ],
      "simple-import-sort/exports": "error",

      // 禁用冲突的规则
      "sort-imports": "off",

      // React 特定规则
      "react/react-in-jsx-scope": "off", // React 17+ 不需要导入 React
      "react/jsx-uses-react": "off", // React 17+ 不需要
      "react/prop-types": "off", // 使用 TypeScript，不需要 prop-types

      // TypeScript 特定规则
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/no-explicit-any": "warn",

      // 通用规则
      "no-console": "warn",
      "no-debugger": "error",
    },
    settings: {
      react: {
        version: "detect",
      },
    },
  },

  // 仅 TypeScript 文件的额外配置
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        project: "./tsconfig.json",
      },
    },
  },

  // 忽略配置
  {
    ignores: [
      "node_modules/**",
      "dist/**",
      "build/**",
      "*.config.js",
      "*.config.ts",
    ],
  },

  // Prettier 兼容性（必须放在最后）
  prettierConfig
);
