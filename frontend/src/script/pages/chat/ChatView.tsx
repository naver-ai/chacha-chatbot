import { yupResolver } from "@hookform/resolvers/yup"
import { EntityId, nanoid } from "@reduxjs/toolkit"
import { useCallback, useEffect, useMemo, useRef } from "react"
import { useForm } from "react-hook-form"
import { useDispatch, useSelector } from "src/script/redux/hooks"
import * as yup from "yup"
import { sendUserMessage } from "./reducer"
import { MessageView } from "src/script/components/messages"
import { CopyToClipboard } from 'react-copy-to-clipboard';
import path from "path"
import { ClipboardDocumentIcon } from "@heroicons/react/20/solid";
import { enqueueSnackbar } from "notistack"
import { EmotionPicker } from "./components/EmotionPicker"
import TextareaAutosize from 'react-textarea-autosize';

export const ChatView = () => {

  const scrollViewRef = useRef<HTMLDivElement>(null)

  const messageIds = useSelector(state => state.chatState.messages.ids)

  const scrollToBottom = useCallback(() => {
    if (scrollViewRef?.current != null) {
      const scroll = scrollViewRef.current.scrollHeight -
        scrollViewRef.current.clientHeight;
      scrollViewRef.current.scrollTo({
        behavior: "smooth",
        top: scroll
      })
    }
  }, [])

  useEffect(() => {
    requestAnimationFrame(() => {
      scrollToBottom()
    })
  }, [messageIds.length])

  return <div className="turn-list-container pt-2 overflow-y-auto justify-end h-full" ref={scrollViewRef}>
    <SessionInfoPanel/>
    <div className="turn-list container mx-auto px-10">{
      messageIds.map((id, i) => {
        return <SessionMessageView key={id.toString()} id={id} isLast={messageIds.length - 1 === i}/>
      })
    }
    </div>
    <TypingPanel />
  </div>
}

const SessionInfoPanel = () => {
  const sessionInfo = useSelector(state => state.chatState.sessionInfo)

  return <div className="container bg-slate-400/20 px-1.5 pr-1 py-1 rounded-md flex justify-between">
          <span>세션 ID: {sessionInfo?.sessionId} ({sessionInfo?.name}, {sessionInfo?.age}세)</span>
          <ShareButton/>
          </div>
}


const schema = yup.object({
  message: yup.string().trim().transform((text:string) => text.replace(/ +/g, " ").replace(/[\r\n]+/g, "\n")).required()
}).required()

const TypingPanel = () => {

  const isSystemMessageLoading = useSelector(state => state.chatState.isLoadingMessage)

  const shouldHideTypingPanel = useSelector(state => {
    const {ids, entities} = state.chatState.messages
    if(ids.length > 0){
      const lastId = ids[ids.length - 1]
      const lastMessage = entities[lastId]
      return (lastMessage?.is_user === false && lastMessage?.metadata?.select_emotion === true)
    }else return false
  })

  const dispatch = useDispatch()

  const {
    register,
    handleSubmit,
    reset,
    setFocus,
  } = useForm({
    resolver: yupResolver(schema),
    reValidateMode: 'onChange'
  })


  const onSubmit = useCallback((data: { message: string }) => {
    if (!isSystemMessageLoading) {
      reset({ message: "" })
      dispatch(sendUserMessage({ id: nanoid(), message: data.message, is_user: true, metadata: undefined, timestamp: Date.now() }))
    }
  }, [isSystemMessageLoading])

  useEffect(() => {
    setFocus('message')
  }, [setFocus])

  return shouldHideTypingPanel ? null : <>
    <div id="chat-typing-panel" className="fixed z-10 left-4 right-4 bottom-10 lg:left-0 lg:right-0">
      <div className="container relative">
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-row bg-slate-50 px-3 py-1.5 pl-1.5 rounded-lg shadow-lg">
          {
            isSystemMessageLoading
              ? <div className="text-input text-chat-1 animate-pulse-fast flex-1 mr-2">할 말을 생각 중이야. 잠시만 기다려줘!</div>
              : <TextareaAutosize {...register("message")} minRows={1} maxRows={5} autoFocus={true} placeholder={"나에게 할 말을 입력해줘!"}
                className="chat-type flex-1 mr-2"
                autoComplete="off"
              />
          }
          <input type="submit" value="보내기" className="button-main" disabled={isSystemMessageLoading} />

        </form>
      </div>


    </div>
    <div className="bg-background/70 fixed bottom-0 left-10 right-10 h-[50px]" /></>
}




const ShareButton = () => {

  const sessionId = useSelector(state => state.chatState.sessionInfo!.sessionId)
  const urlOrigin = useMemo(() => new URL(window.location.href).origin, [])
  const shareURL = useMemo(() => {
    return path.join(urlOrigin, "share", sessionId)
  }, [urlOrigin, sessionId])

  const onCopy = useCallback((text: string, result: boolean) => {
    enqueueSnackbar('링크가 클립보드에 복사되었습니다.', {
      autoHideDuration: 1000,
      preventDuplicate: true
    })
  }, [])

  return <CopyToClipboard text={shareURL} onCopy={onCopy}>
    <button className="button-clear button-tiny button-with-icon opacity-70">
      <ClipboardDocumentIcon className="w-4 mr-1 opacity-70" />
      <span>링크 공유하기</span>
    </button></CopyToClipboard>
}

const SessionMessageView = (props: { id: EntityId, isLast: boolean }) => {
  const turn = useSelector(state => state.chatState.messages.entities[props.id]!)

  const hideMessage = turn.metadata?.hide === true

  const isEmotionSelectionTurn = turn.metadata?.select_emotion === true

  return hideMessage ? null : <MessageView message={turn} componentsBelowCallout={
      !isEmotionSelectionTurn
        ? null : <EmotionPicker messageId={props.id} disabled={!props.isLast}/>
    }/>
}
