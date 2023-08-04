import { useEffect } from "react"
import { useParams } from "react-router-dom"
import { BackgroundPanel } from "src/script/components/background"
import { useSelector, useDispatch } from "src/script/redux/hooks"
import { loadChatSession } from "./reducer"
import { EntityId } from "@reduxjs/toolkit"
import { MessageView } from "src/script/components/messages"
import { EMOTION_LIST } from "src/script/concepts"

export const ChatSharePage = () => {
    const { sessionId } = useParams()

    const isLoading = useSelector(state => state.chatShareState.isLoading)

    const messageIds = useSelector(state => state.chatShareState.messages.ids)

    const dispatch = useDispatch()

    useEffect(() => {
        if (sessionId != null) {
            dispatch(loadChatSession(sessionId))
        }
    }, [sessionId])

    return <div className="h-screen overflow-y-auto">
        <div className="turn-list container mx-auto px-10 mb-10 mt-3">
            {
                messageIds.map(id => <SessionMessageView key={id.toString()} id={id} />)
            }
        </div>
        <BackgroundPanel />
    </div>
}


const SessionMessageView = (props: { id: EntityId }) => {
    const turn = useSelector(state => state.chatShareState.messages.entities[props.id]!)

    const isEmotionAnswerTurn = Array.isArray(turn.metadata?.selected_emotions) && turn.is_user === true

    return <MessageView message={turn} hideCallout={isEmotionAnswerTurn}
        componentsAboveCallout={isEmotionAnswerTurn ? <EmotionSelectionView selected={turn.metadata?.selected_emotions}/>: null} />
}

const EmotionSelectionView = (props: { selected: Array<string> }) => {

    return <div className="emolist">
        {
            EMOTION_LIST.map(em => {
                return <span className="emotion view-only" aria-disabled={true} aria-selected={props.selected.indexOf(em.en) >= 0} key={em.en}>{em.kr} {em.emoji}</span>
            })
        }      
    </div>
}