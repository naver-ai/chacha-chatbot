export interface ChatMessage{
    id: string
    message: string
    is_user: boolean
    metadata?: { [key:string]: any } | undefined
    processing_time?: number | undefined
    timestamp: number
}

