import { z } from "zod";

// Login form validation schema
export const loginSchema = z.object({
  name: z.string()
    .min(1, "用户名不能为空")
    .max(50, "用户名不能超过50个字符"),
  password: z.string()
    .min(1, "密码不能为空")
    .max(128, "密码不能超过128个字符")
});

// Register form validation schema
export const registerSchema = z.object({
  name: z.string()
    .min(3, "用户名至少需要3个字符")
    .max(50, "用户名不能超过50个字符")
    .regex(/^[a-zA-Z0-9_-]+$/, "用户名只能包含字母、数字、下划线和连字符")
    .refine(val => !val[0]?.match(/\d/), "用户名不能以数字开头"),
  password: z.string()
    .min(6, "密码至少需要6个字符")
    .max(128, "密码不能超过128个字符")
    .refine(val => {
      const weakPatterns = ['123456', 'password', 'qwerty', '111111'];
      return !weakPatterns.some(pattern => val.toLowerCase().includes(pattern));
    }, "密码过于简单，请使用更复杂的密码"),
  nickname: z.string()
    .min(1, "昵称不能为空")
    .max(50, "昵称不能超过50个字符")
    .optional(),
  email: z.string()
    .email("请输入有效的邮箱地址")
    .optional()
    .or(z.literal("")),
  phone: z.string()
    .refine(val => !val || /^1[3-9]\d{9}$/.test(val), "请输入有效的中国大陆手机号码")
    .optional()
    .or(z.literal(""))
});

// Types based on the schemas
export type LoginFormValues = z.infer<typeof loginSchema>;
export type RegisterFormValues = z.infer<typeof registerSchema>;
