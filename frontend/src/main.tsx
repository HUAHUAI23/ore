import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import { I18nextProvider } from 'react-i18next'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createRouter, RouterProvider } from '@tanstack/react-router'

import { Toaster } from "@/components/ui/sonner"
import { ThemeProvider } from "@/provider/theme-provider"

import { ConstantCategory, getConstant } from './constant/index.ts'
import i18n from './i18n'
import reportWebVitals from './reportWebVitals.ts'
// Import the generated route tree
import { routeTree } from './routeTree.gen'

import './styles.css'

// Create a new router instance
const router = createRouter({
  routeTree,
  context: {},
  defaultPreload: 'intent',
  scrollRestoration: true,
  defaultStructuralSharing: true,
  defaultPreloadStaleTime: 0,
})

// Register the router instance for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: getConstant(ConstantCategory.FEATURE, 'QUERY_STALE_TIME', 5 * 60 * 1000),
      retry: getConstant(ConstantCategory.FEATURE, 'DEFAULT_QUERY_RETRY', 1),
      refetchOnWindowFocus: false
    }
  }
})
// Render the app
const rootElement = document.getElementById('app')
if (rootElement && !rootElement.innerHTML) {
  const root = ReactDOM.createRoot(rootElement)
  root.render(
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <I18nextProvider i18n={i18n}>
          <ThemeProvider defaultTheme="system" storageKey="ore-theme">
            <RouterProvider router={router} />
            <Toaster />
          </ThemeProvider>
        </I18nextProvider>
      </QueryClientProvider>
    </StrictMode>,
  )
}

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals()
