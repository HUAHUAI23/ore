// .prettierrc.js
module.exports = {
    // 基础配置
    semi: true,
    singleQuote: true,
    tabWidth: 2,
    useTabs: false,
    trailingComma: 'es5',
    bracketSpacing: true,
    bracketSameLine: false,
    arrowParens: 'avoid',

    // 换行配置
    printWidth: 80,
    endOfLine: 'lf',

    // JSX 配置
    jsxSingleQuote: false,

    // 文件匹配
    overrides: [
        {
            files: '*.{ts,tsx,js,jsx}',
            options: {
                parser: 'typescript',
            },
        },
        {
            files: '*.{css,scss,less}',
            options: {
                parser: 'css',
            },
        },
        {
            files: '*.json',
            options: {
                parser: 'json',
            },
        },
    ],
}