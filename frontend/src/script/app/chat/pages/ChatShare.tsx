import { useCallback, useEffect } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { BackgroundPanel } from "src/script/components/background"
import { useSelector, useDispatch } from "src/script/redux/hooks"
import { EntityId } from "@reduxjs/toolkit"
import { MessageView } from "src/script/components/messages"
import { EMOTION_LIST } from "src/script/concepts"
import { SessionInfoPanel } from "../../../components/SessionInfoPanel"
import { loadChatSession } from "../reducer"
import { TableCellsIcon } from "@heroicons/react/20/solid"
import { NetworkHelper } from "src/script/network"
import FileSaver from 'file-saver'
import { useTranslation } from "react-i18next"

export const ChatSharePage = () => {
    const { sessionId } = useParams()

    const isLoading = useSelector(state => state.chatState.isLoadingMessage)

    const messageIds = useSelector(state => state.chatState.messages.ids)

    const dispatch = useDispatch()

    useEffect(() => {
        if (sessionId != null) {
            dispatch(loadChatSession(sessionId))
        }
    }, [sessionId])

    return <div className="h-screen overflow-y-auto">
        {
            isLoading === true ? <div>Loading....</div> : <>
            <ChatSessionInfoPanel/>
            <div className="turn-list container mx-auto px-10 mb-10 mt-3">
            {
                messageIds.map(id => <SessionMessageView key={id.toString()} id={id} />)
            }
        </div>
        </>
        }
        <BackgroundPanel />
    </div>
}


const SessionMessageView = (props: { id: EntityId }) => {
    const userName = useSelector(state => state.chatState.sessionInfo!.name!)
    const turn = useSelector(state => state.chatState.messages.entities[props.id]!)

    const isEmotionAnswerTurn = Array.isArray(turn.metadata?.selected_emotions) && turn.is_user === true

    return <MessageView avatarHash={turn.is_user === true ? userName : 'system'} message={turn} hideCallout={isEmotionAnswerTurn}
        componentsAboveCallout={isEmotionAnswerTurn ? <EmotionSelectionView selected={turn.metadata?.selected_emotions}/>: null} />
}

const ChatSessionInfoPanel = () => {
    const sessionId = useSelector(state => state.chatState.sessionInfo?.sessionId!)
    const userName = useSelector(state => state.chatState.sessionInfo?.name!)
    const userAge = useSelector(state => state.chatState.sessionInfo?.age!)

    const onDownloadClick = useCallback(async ()=>{
        const resp = await fetch(NetworkHelper.makeEndpoint(sessionId, NetworkHelper.ENDPOINT_DOWNLOAD_CSV),
        {
            method: 'GET'
        })
        const blob = await resp.blob()
        FileSaver.saveAs(blob, `session_${sessionId}.csv`)
    }, [])

    const [t] = useTranslation()
  
    return <SessionInfoPanel sessionId={sessionId} name={userName} age={userAge}>
            
        <button className="button-clear button-tiny button-with-icon opacity-70" onClick={onDownloadClick}>
            <TableCellsIcon className="w-4 mr-1 opacity-70" />
            <span>{t("SHARE.SAVE")}</span>
        </button>
    </SessionInfoPanel>
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