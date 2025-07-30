// src/vite-env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly MODE: string
    readonly BASE_URL: string
    readonly DEV: boolean
    readonly PROD: boolean
    readonly SSR: boolean

    // 自定义环境变量
    readonly VITE_API_BASE_URL?: string
    readonly VITE_API_TIMEOUT?: string
    // 添加更多自定义环境变量
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}