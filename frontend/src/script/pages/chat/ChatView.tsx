import { yupResolver } from "@hookform/resolvers/yup"
import { EntityId, nanoid } from "@reduxjs/toolkit"
import { useCallback, useEffect, useMemo, useRef, useState, KeyboardEvent, FocusEvent } from "react"
import { useForm } from "react-hook-form"
import { useDispatch, useSelector } from "src/script/redux/hooks"
import * as yup from "yup"
import { sendUserMessage } from "./reducer"
import { MessageView } from "src/script/components/messages"
import { CopyToClipboard } from 'react-copy-to-clipboard';
import path from "path"
import { ClipboardDocumentIcon, PaperAirplaneIcon } from "@heroicons/react/20/solid";
import { enqueueSnackbar } from "notistack"
import { EmotionPicker } from "./components/EmotionPicker"
import TextareaAutosize from 'react-textarea-autosize';
import { useMediaQuery } from "react-responsive"
import { useOnScreenKeyboardScrollFix, useViewportSize } from "src/script/mobile-utils"

const mobileMediaQuery = { minWidth: 640 }
function useIsMobile(): boolean{
  return useMediaQuery(mobileMediaQuery) === false
}

export const ChatView = () => {

  const desktopScrollViewRef = useRef<HTMLDivElement>(null)
  const mobileScrollViewRef = useRef<HTMLDivElement>(null)

  const isMobile = useIsMobile()
  console.log(isMobile)

  useOnScreenKeyboardScrollFix(isMobile)


  const messageIds = useSelector(state => state.chatState.messages.ids)

  const [_, viewPortHeight] = useViewportSize()

  const scrollToBottom = useCallback(() => {

    const scrollViewRef = isMobile === true ? mobileScrollViewRef : desktopScrollViewRef
    if (scrollViewRef?.current != null) {
      const scroll = scrollViewRef.current.scrollHeight -
        scrollViewRef.current.clientHeight;
      scrollViewRef.current.scrollTo({
        behavior: "smooth",
        top: scroll
      })
    }
  }, [isMobile])

  const onTypingPanelFocus = useCallback(()=>{
    
    requestAnimationFrame(()=>{
      if(isMobile === true){
        setTimeout(scrollToBottom, 1010)
      }
    })
  }, [scrollToBottom, isMobile])

  useEffect(() => {
    requestAnimationFrame(() => {
      scrollToBottom()
    })
  }, [messageIds.length])

  return <div style={isMobile === true ? {maxHeight: viewPortHeight, height: viewPortHeight, minHeight: viewPortHeight} : undefined} className="overflow-hidden turn-list-container sm:overflow-y-auto justify-end h-screen sm:h-full flex flex-col sm:block" 
    ref={desktopScrollViewRef}>
    <SessionInfoPanel/>
    <div className="turn-list container mx-auto px-3 sm:px-10 flex-1 overflow-y-auto sm:overflow-visible"
    ref={mobileScrollViewRef}
    >{
      messageIds.map((id, i) => {
        return <SessionMessageView key={id.toString()} id={id} isLast={messageIds.length - 1 === i}/>
      })
    }
    </div>
    <TypingPanel onFocus={onTypingPanelFocus}/>
  </div>
}

const SessionInfoPanel = () => {
  const sessionInfo = useSelector(state => state.chatState.sessionInfo)

  return <div className="container bg-slate-400/20 px-1.5 pr-1 py-1 flex items-center justify-between text-xs sm:text-sm sm:mt-2 sm:rounded-md border-collapse border-b-2 sm:border-none border-slate-300">
          <div>세션: {sessionInfo?.sessionId} ({sessionInfo?.name}, {sessionInfo?.age}세)</div>
          <ShareButton/>
          </div>
}


const schema = yup.object({
  message: yup.string().trim().transform((text:string) => text.replace(/ +/g, " ").replace(/[\r\n]+/g, "\n")).required()
}).required()

const TypingPanel = (props: {
  onFocus?: ()=>void,
  onBlur?: ()=>void
}) => {

  const isSystemMessageLoading = useSelector(state => state.chatState.isLoadingMessage)

  const shouldHideTypingPanel = useSelector(state => {
    const {ids, entities} = state.chatState.messages
    if(ids.length > 0){
      const lastId = ids[ids.length - 1]
      const lastMessage = entities[lastId]
      return (lastMessage?.is_user === false && lastMessage?.metadata?.select_emotion === true)
    }else return false
  })

  const isMobile = useIsMobile()

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


  const handleKeyDownOnNameField = useCallback((ev: KeyboardEvent<HTMLTextAreaElement>)=>{
    if(isMobile === false && ev.key == 'Enter' && ev.shiftKey === false){
      ev.preventDefault()
      handleSubmit(onSubmit)()
    }
}, [isMobile, handleSubmit, onSubmit])

  const onTypingViewFocusIn = useCallback((ev: FocusEvent<HTMLTextAreaElement, Element>)=>{
    props.onFocus?.()
  }, [props.onFocus])

  const onTypingViewFocusOut = useCallback((ev: FocusEvent<HTMLTextAreaElement, Element>)=>{
    props.onBlur?.()
  }, [props.onBlur])

  useEffect(() => {
    setFocus('message')
  }, [setFocus])

  return shouldHideTypingPanel ? null : <>
    <div id="chat-typing-panel" className="sm:fixed sm:z-10 sm:left-4 sm:right-4 sm:bottom-10 lg:left-0 lg:right-0">
      <div className="container relative">
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-row bg-slate-50 px-3 py-1.5 pl-1.5 sm:rounded-lg shadow-lg">
          {
            isSystemMessageLoading
              ? <div className="text-input text-chat-1 animate-pulse-fast flex-1 mr-2">할 말을 생각 중이야. 잠시만 기다려줘!</div>
              : <TextareaAutosize {...register("message")} minRows={1} maxRows={5} autoFocus={true} placeholder={"나에게 할 말을 입력해줘!"}
                className="chat-type flex-1 mr-2"
                autoComplete="off"
                onFocus={onTypingViewFocusIn}
                onBlur={onTypingViewFocusOut}
                onKeyDown={handleKeyDownOnNameField}
              />
          }
          <button type="submit" className="button-main" disabled={isSystemMessageLoading}>
            {
              isMobile ? <PaperAirplaneIcon className="w-5"/> : <span>보내기</span>
            }
          </button>

        </form>
      </div>


    </div>
    <div className="bg-background/70 fixed bottom-0 left-10 right-10 h-[50px] collapse sm:visible" /></>
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
