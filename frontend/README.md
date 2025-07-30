# ORE Frontend

React + TypeScript frontend application for the ORE AI workflow engine, built with modern development tools and best practices.

## Tech Stack

- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite 6 with HMR and code splitting
- **Routing**: TanStack Router (file-based routing)
- **State Management**: 
  - TanStack Query for server state
  - Zustand for client state
- **Styling**: Tailwind CSS v4 + shadcn/ui components
- **Internationalization**: i18next with React integration
- **HTTP Client**: Axios for API requests
- **Forms**: React Hook Form with Zod validation
- **Testing**: Vitest + React Testing Library
- **Code Quality**: ESLint + Prettier + TypeScript

## Project Structure

```
frontend/
├── public/                 # Static assets
│   ├── locales/           # Translation files
│   │   ├── en/            # English translations
│   │   └── zh/            # Chinese translations
│   └── favicon.ico
├── src/
│   ├── api/               # API client and services
│   ├── components/        # Reusable UI components
│   │   └── ui/            # shadcn/ui components
│   ├── constant/          # Application constants
│   ├── feature/           # Feature-specific components
│   │   └── auth/          # Authentication components
│   ├── hooks/             # Custom React hooks
│   ├── lib/               # Utility libraries
│   ├── provider/          # React context providers
│   ├── routes/            # File-based route definitions
│   ├── store/             # Zustand state stores
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   ├── validation/        # Zod validation schemas
│   ├── i18n.ts            # i18next configuration
│   ├── main.tsx           # Application entry point
│   └── styles.css         # Global styles
├── components.json        # shadcn/ui configuration
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── vite.config.ts         # Vite build configuration
└── README.md             # This file
```

## Getting Started

### Prerequisites

- Node.js 18+ or Bun
- Backend server running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
bun install

# Or with npm
npm install
```

### Development

```bash
# Start development server
bun run dev

# Or with npm
npm run dev
```

The application will be available at `http://localhost:3000`.

### Environment Variables

Create environment files for different environments:

```bash
# Copy template
cp .env.template .env.development

# Edit variables
# VITE_API_BASE_URL=http://localhost:8000
```

## Available Scripts

```bash
# Development
bun run dev              # Start dev server on port 3000
bun run start            # Alias for dev

# Production
bun run build            # Build for production
bun run serve            # Preview production build

# Testing
bun run test             # Run tests with Vitest

# Code Quality
bun run lint             # Check linting issues
bun run lint:fix         # Auto-fix linting issues
bun run format           # Format code with Prettier
bun run format:check     # Check code formatting
bun run check            # Run both lint and format checks
bun run fix              # Fix both lint and format issues
```

## Key Features

### Authentication

The app includes a complete authentication system:

- User registration and login
- JWT token management
- Protected routes
- Automatic token refresh
- State persistence

```tsx
// Example: Using auth in components
import { useAuthStore } from '@/store/auth'

function Dashboard() {
  const { user, isAuthenticated, logout } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />
  }
  
  return <div>Welcome, {user?.email}</div>
}
```

### API Integration

Centralized API client with automatic token injection:

```tsx
// Example: Making API calls
import { api } from '@/api'
import { useQuery } from '@tanstack/react-query'

function UserProfile() {
  const { data: user, isLoading } = useQuery({
    queryKey: ['user', 'profile'],
    queryFn: () => api.get('/user/profile')
  })
  
  if (isLoading) return <div>Loading...</div>
  return <div>{user.name}</div>
}
```

### Internationalization

Multi-language support with automatic language detection:

```tsx
// Example: Using translations
import { useTranslation } from 'react-i18next'

function Welcome() {
  const { t, i18n } = useTranslation()
  
  return (
    <div>
      <h1>{t('welcome.title')}</h1>
      <button onClick={() => i18n.changeLanguage('zh')}>
        中文
      </button>
    </div>
  )
}
```

### UI Components

Built with shadcn/ui for consistent, accessible design:

```bash
# Add new components
bunx shadcn@latest add button
bunx shadcn@latest add dialog
bunx shadcn@latest add form
```

```tsx
// Example: Using UI components
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

function LoginForm() {
  return (
    <form>
      <Input placeholder="Email" />
      <Button type="submit">Login</Button>
    </form>
  )
}
```

### Routing

File-based routing with type-safe navigation:

```tsx
// routes/dashboard.tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/dashboard')({
  component: Dashboard,
  beforeLoad: ({ context }) => {
    if (!context.auth.isAuthenticated) {
      throw redirect({ to: '/login' })
    }
  }
})

function Dashboard() {
  return <div>Dashboard Content</div>
}
```

### State Management

Zustand for simple, scalable state management:

```tsx
// store/auth.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: async (credentials) => {
        const { user, token } = await api.login(credentials)
        set({ user, token, isAuthenticated: true })
      },
      logout: () => {
        set({ user: null, token: null, isAuthenticated: false })
      }
    }),
    { name: 'auth-storage' }
  )
)
```

## Development Guidelines

### Code Organization

- **Components**: Keep components small and focused on a single responsibility
- **Hooks**: Extract complex logic into custom hooks
- **Types**: Define TypeScript interfaces for all data structures
- **API**: Centralize API calls in the `api/` directory
- **State**: Use Zustand for client state, TanStack Query for server state

### Styling Guidelines

- Use Tailwind CSS utility classes for styling
- Follow shadcn/ui design patterns for consistency
- Use CSS variables for theming support
- Prefer composition over custom CSS

### Testing Strategy

- Write unit tests for utility functions
- Test components with React Testing Library
- Focus on user interactions and behaviors
- Mock API calls in tests

```tsx
// Example: Component test
import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { LoginForm } from './LoginForm'

test('submits form with user credentials', async () => {
  const user = userEvent.setup()
  const onSubmit = vi.fn()
  
  render(<LoginForm onSubmit={onSubmit} />)
  
  await user.type(screen.getByLabelText(/email/i), 'user@example.com')
  await user.type(screen.getByLabelText(/password/i), 'password123')
  await user.click(screen.getByRole('button', { name: /login/i }))
  
  expect(onSubmit).toHaveBeenCalledWith({
    email: 'user@example.com',
    password: 'password123'
  })
})
```

### Performance Considerations

- Use React.memo() for expensive components
- Implement code splitting with React.lazy()
- Optimize bundle size with dynamic imports
- Use TanStack Query for efficient data fetching and caching

## Building for Production

```bash
# Build the application
bun run build

# Preview the build
bun run serve
```

The build output will be in the `dist/` directory, ready for deployment to any static hosting service.

## Deployment

The frontend is a static React application that can be deployed to:

- Vercel (recommended for Vite projects)
- Netlify
- GitHub Pages
- AWS S3 + CloudFront
- Any static hosting service

Make sure to configure environment variables for production:

```bash
# Production environment variables
VITE_API_BASE_URL=https://your-api-domain.com
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the existing code style and patterns
2. Write tests for new features
3. Update documentation when adding new functionality
4. Use meaningful commit messages
5. Run linting and formatting before committing

## Troubleshooting

### Common Issues

**Build Errors**: Check TypeScript types and import paths
**API Connection**: Verify backend server is running and CORS is configured
**Translation Missing**: Check translation keys exist in all language files
**Style Issues**: Ensure Tailwind classes are properly configured

### Development Tips

- Use React DevTools for debugging component state
- Use TanStack Query DevTools for API debugging
- Check browser console for runtime errors
- Use TypeScript strict mode for better error catching