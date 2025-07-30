declare global {
    // 为 window 添加 ApiError 类型
    // interface Window {
    //     ApiError: typeof import('../api').ApiError
    // }

    // 直接声明全局类型
    type ApiError = import('../api').ApiError
}

// 这个导出是必需的，让这个文件被视为一个模块
export { }
