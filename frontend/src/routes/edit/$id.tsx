import { createFileRoute } from '@tanstack/react-router'
import { motion } from 'framer-motion'

import { WorkflowEditorPage } from '@/feature/workflow/components/workflow-editor-page'

export const Route = createFileRoute('/edit/$id')({
    component: WorkflowEditorComponent,
})

function WorkflowEditorComponent() {
    const { id } = Route.useParams()
    const workflowId = parseInt(id, 10)
    console.log('WorkflowEditorComponent', workflowId)
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="h-screen"
        >
            <WorkflowEditorPage workflowId={workflowId} />
        </motion.div>
    )
}