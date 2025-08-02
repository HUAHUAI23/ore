import { createFileRoute } from '@tanstack/react-router'
import { motion } from 'framer-motion'

import { WorkflowsPage } from '@/feature/workflow/components/workflows-page'

export const Route = createFileRoute('/workflows')({
    component: WorkflowsComponent,
})

function WorkflowsComponent() {
    console.log('WorkflowsComponent')
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="h-screen"
        >
            <WorkflowsPage />
        </motion.div>
    )
}