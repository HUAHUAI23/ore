import { ENV } from "@/utils/env";

/**
 * 常量类型定义
 */
export type ConstantValue = string | number | boolean | null | undefined;

/**
 * 常量分类枚举
 */
export enum ConstantCategory {
  SYSTEM = "system",
  UI = "ui",
  CONFIG = "config",
  FEATURE = "feature",
}

/**
 * 常量存储接口
 */
interface ConstantStore {
  [category: string]: {
    [key: string]: ConstantValue;
  };
}

/**
 * 常量存储对象
 * 使用分类存储不同类型的常量
 */
const constantStore: ConstantStore = {
  [ConstantCategory.SYSTEM]: {
    VERSION: "1.0.0",
    API_TIMEOUT: Number(ENV.API_TIMEOUT),
    DEBUG_MODE: ENV.isDevelopment,
  },
  [ConstantCategory.UI]: {
    DEFAULT_THEME: "light",
    // MOBILE_BREAKPOINT: 768,
  },
  [ConstantCategory.CONFIG]: {
    DEFAULT_PAGE_SIZE: 10,
    MAX_PASSWORD_LENGTH: 20,
    MIN_PASSWORD_LENGTH: 8,
  },
  [ConstantCategory.FEATURE]: {
    QUERY_STALE_TIME: 5 * 60 * 1000,
    DEFAULT_QUERY_RETRY: 1,
    TOAST_DURATION: 2000,
    // LOG_RETENTION_DAYS: 90,
  },
};

/**
 * 常量获取函数
 * @param category 常量分类
 * @param key 常量键名
 * @param defaultValue 默认值（当常量不存在时返回）
 * @returns 常量值或默认值
 */
export function getConstant<T extends ConstantValue>(
  category: ConstantCategory,
  key: string,
  defaultValue?: T
): T {
  if (constantStore[category] && constantStore[category][key] !== undefined) {
    return constantStore[category][key] as T;
  }
  return defaultValue as T;
}

/**
 * 常量设置函数
 * @param category 常量分类
 * @param key 常量键名
 * @param value 要设置的值
 * @returns 是否设置成功
 */
export function setConstant(
  category: ConstantCategory,
  key: string,
  value: ConstantValue
): boolean {
  try {
    // 确保分类存在
    if (!constantStore[category]) {
      constantStore[category] = {};
    }

    // 设置常量值
    constantStore[category][key] = value;
    return true;
  } catch (error) {
    console.error(`Failed to set constant [${category}.${key}]:`, error);
    return false;
  }
}

/**
 * 检查常量是否存在
 * @param category 常量分类
 * @param key 常量键名
 * @returns 是否存在
 */
export function hasConstant(category: ConstantCategory, key: string): boolean {
  return (
    constantStore[category] !== undefined &&
    constantStore[category][key] !== undefined
  );
}

/**
 * 获取分类下的所有常量
 * @param category 常量分类
 * @returns 常量对象
 */
export function getCategoryConstants(
  category: ConstantCategory
): Record<string, ConstantValue> {
  return constantStore[category] || {};
}

/**
 * 批量设置常量
 * @param category 常量分类
 * @param constants 常量键值对
 * @returns 是否全部设置成功
 */
export function setBatchConstants(
  category: ConstantCategory,
  constants: Record<string, ConstantValue>
): boolean {
  try {
    // 确保分类存在
    if (!constantStore[category]) {
      constantStore[category] = {};
    }

    // 批量设置常量
    Object.entries(constants).forEach(([key, value]) => {
      constantStore[category][key] = value;
    });

    return true;
  } catch (error) {
    console.error(
      `Failed to set batch constants for category [${category}]:`,
      error
    );
    return false;
  }
}
