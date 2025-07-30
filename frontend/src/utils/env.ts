// src/utils/env.ts
// 定义一个安全的环境访问方法，避免直接使用process.env
export const ENV = {
    NODE_ENV: import.meta.env.MODE || 'development',
    isDevelopment: import.meta.env.DEV,
    isProduction: import.meta.env.PROD,
    // 添加其他需要的环境变量
    API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
    API_TIMEOUT: import.meta.env.VITE_API_TIMEOUT,
    // 如果有其他环境变量，也可以在这里添加
}