import { useEffect } from "react"
import { useParams } from "react-router-dom"
import { BackgroundPanel } from "src/script/components/background"
import { useSelector, useDispatch } from "src/script/redux/hooks"
import { loadChatSession } from "./reducer"
import { EntityId } from "@reduxjs/toolkit"
import { MessageView } from "src/script/components/messages"

export const ChatSharePage = () => {
    const { sessionId } = useParams()

    const isLoading = useSelector(state => state.chatShareState.isLoading)

    const messageIds = useSelector(state => state.chatShareState.messages.ids)

    const dispatch = useDispatch()

    useEffect(()=>{
        if(sessionId != null){
            dispatch(loadChatSession(sessionId))
        }
    }, [sessionId])
    
    return <div className="h-screen overflow-y-auto">
        <div className="turn-list container mx-auto px-10 mb-10 mt-3">
            {
                messageIds.map(id => <SessionMessageView key={id.toString()} id={id}/>)
            }
        </div>
        <BackgroundPanel/>
    </div>
}



const SessionMessageView = (props: { id: EntityId }) => {
    const turn = useSelector(state => state.chatShareState.messages.entities[props.id]!)
  
    return <MessageView message={turn}/>
  }