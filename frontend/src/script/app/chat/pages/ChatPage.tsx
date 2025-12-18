import { IntroView } from "../components/IntroView";
import { useEffect, useRef, useState } from "react";
import { nanoid } from "nanoid";
import { useDispatch, useSelector } from "../../../redux/hooks";
import { BackgroundPanel } from "src/script/components/background";
import { useNavigate, useParams } from "react-router-dom";

import { yupResolver } from "@hookform/resolvers/yup"
import { EntityId } from "@reduxjs/toolkit"
import { useCallback, useMemo, KeyboardEvent, FocusEvent } from "react"
import { useForm } from "react-hook-form"
import * as yup from "yup"
import { loadChatSession, regenerateLastSystemMessage, selectInitialMessageTimestamp, sendUserMessage } from "../reducer"
import { MessageView } from "src/script/components/messages"
import { CopyToClipboard } from 'react-copy-to-clipboard';
import path from "path"
import { ClipboardDocumentIcon, PaperAirplaneIcon } from "@heroicons/react/20/solid";
import { enqueueSnackbar } from "notistack"
import TextareaAutosize from 'react-textarea-autosize';
import { useMediaQuery } from "react-responsive"
import { useOnScreenKeyboardScrollFix, useViewportSize } from "src/script/mobile-utils"
import { SessionInfoPanel } from "../../../components/SessionInfoPanel"
import { EmotionPicker } from "../components/EmotionPicker";
import useAsyncEffect from 'use-async-effect';
import { NetworkHelper } from "src/script/network";
import { useTranslation } from "react-i18next";
import { twMerge } from "tailwind-merge";
const format = require('string-format')
import {HomeIcon} from '@heroicons/react/20/solid'
import useApp from "antd/es/app/useApp";

const RESET_TIME_LIMIT_MILLIS = 2 * 60 * 1000 // 2 minutes

export const ChatPage = () => {

  const { sessionId } = useParams()

  const sessionInfoExists = useSelector(state => state.chatState.sessionInfo != null)

  const dispatch = useDispatch()

  useAsyncEffect(async isMounted => {
    if(sessionId != null){
      try{
        const sessionInfo = await NetworkHelper.loadSessionInfo(sessionId)
        if(isMounted() == true) {
        // session info exists.
        dispatch(loadChatSession(sessionId, true))
      }
    }catch(ex){

    }
  }
}, [sessionId])


  return <>
    {
      sessionInfoExists ? <ChatView /> : <IntroView sessionId={sessionId!}/>
    }
    <BackgroundPanel showVignette={sessionInfoExists} scrollContainer={sessionInfoExists ? "chat-scroll" : undefined} />
  </>
}


const mobileMediaQuery = { minWidth: 640 }
function useIsMobile(): boolean{
  return useMediaQuery(mobileMediaQuery) === false
}

const ChatView = () => {

  const desktopScrollViewRef = useRef<HTMLDivElement>(null)
  const mobileScrollViewRef = useRef<HTMLDivElement>(null)

  const isMobile = useIsMobile()

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
        setTimeout(scrollToBottom, 200)
      }
    })
  }, [scrollToBottom, isMobile])

  useEffect(() => {
    requestAnimationFrame(() => {
      scrollToBottom()
    })
  }, [messageIds.length])

  return <div style={isMobile === true ? {maxHeight: viewPortHeight, height: viewPortHeight, minHeight: viewPortHeight} : undefined} className="overflow-hidden turn-list-container sm:overflow-y-auto justify-end h-screen sm:h-full flex flex-col sm:block" 
    ref={desktopScrollViewRef}
    id={isMobile === false ? "chat-scroll" : undefined}>
    <ChatSessionInfoPanel/>
    <div className="turn-list container mx-auto px-5 flex-1 overflow-y-auto sm:overflow-visible"
    ref={mobileScrollViewRef}
    id={isMobile === true ? "chat-scroll" : undefined}
    >{
      messageIds.map((id, i) => {
        return <SessionMessageView key={id.toString()} id={id} isLast={messageIds.length - 1 === i}/>
      })
    }
    </div>
    <TypingPanel onFocus={onTypingPanelFocus}/>
  </div>
}

const ResetTimer = ({ 
  initialTimestamp, 
  className, 
  overTimeClassName
 }: { initialTimestamp: number | null | undefined, className?: string, overTimeClassName?: string }) => {
  const [time, setTime] = useState<number>(0)
  const [isOvertime, setIsOvertime] = useState<boolean>(false)

  useEffect(() => {
    if (initialTimestamp === null || initialTimestamp === undefined) return

    const updateTimer = () => {
      const now = Date.now()
      const elapsed = now - initialTimestamp
      const remaining = RESET_TIME_LIMIT_MILLIS - elapsed
      
      if (remaining > 0) {
        setTime(Math.ceil(remaining / 1000)) // Convert to seconds
        setIsOvertime(false)
      } else {
        setTime(Math.ceil(Math.abs(remaining) / 1000)) // Show overtime in seconds
        setIsOvertime(true)
      }
    }

    // Update immediately
    updateTimer()

    // Set up interval to update every second
    const interval = setInterval(updateTimer, 1000)

    return () => clearInterval(interval)
  }, [initialTimestamp])

  if (initialTimestamp === null || initialTimestamp === undefined) return null

  const minutes = Math.floor(time / 60)
  const seconds = time % 60

  const combinedClassName = twMerge(className, 
      (isOvertime && overTimeClassName) ? overTimeClassName : "")

  return (
    <div className={combinedClassName}>
      {isOvertime ? '+' : ''}{minutes}:{seconds.toString().padStart(2, '0')}
    </div>
  )
}

const ChatSessionInfoPanel = () => {
  const sessionInfo = useSelector(state => state.chatState.sessionInfo)

  const initialMessageTimestamp = useSelector(selectInitialMessageTimestamp)

  const [t] = useTranslation()

  const navigate = useNavigate()

  const profile = useMemo(()=>format(t("SESSION_INFO.PROFILE_FORMAT"), {name: sessionInfo!.name, age: sessionInfo!.age}), [t, sessionInfo!.name, sessionInfo!.age])

  const antdApp = useApp()

  const onResetClick = useCallback(async ()=>{
    if(await antdApp.modal.confirm({
      content: t("CHAT.CONFIRM_RESET_SESSION"),
      okText: t("LABEL.YES"),
      cancelText: t("LABEL.NO"),
      okType: 'danger'
    })){
      navigate("/")
    }
  }, [t, navigate, antdApp])

  return <SessionInfoPanel sessionId={sessionInfo!.sessionId} name={sessionInfo!.name} age={sessionInfo!.age}>
      <div className="flex gap-x-4 items-center"><div>{profile}</div>
        <ResetTimer initialTimestamp={initialMessageTimestamp} className="" overTimeClassName="text-red-500/70" />
        <HomeIcon className="w-5 h-5 hover:opacity-80 transition-opacity cursor-pointer" title={t("CHAT.RESET_SESSION")} onClick={onResetClick}/>
      </div>
    </SessionInfoPanel>
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
      return (lastMessage?.is_user === false && lastMessage?.metadata?.select_emotion === true) && !state.chatState.isLoadingMessage
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

  const [t] = useTranslation()

  useEffect(() => {
    setFocus('message')
  }, [setFocus])

  return shouldHideTypingPanel ? null : <>
    <div id="chat-typing-panel" className="sm:fixed sm:z-10 sm:left-4 sm:right-4 sm:bottom-16 lg:left-0 lg:right-0">
      <div className="container relative">
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-row frame-bg frame-transparent px-2 py-2 sm:rounded-lg shadow-xl shadow-violet-900/20 border-[1px]">
          {
            isSystemMessageLoading
              ? <div className="text-input text-chat-1 animate-pulse-fast flex-1 mr-2">{t("CHAT.PROCESSING")}</div>
              : <TextareaAutosize {...register("message")} minRows={1} maxRows={5} autoFocus={true} placeholder={t("CHAT.INPUT_PLACEHOLDER")}
                className="chat-type flex-1 mr-2"
                autoComplete="off"
                onFocus={onTypingViewFocusIn}
                onBlur={onTypingViewFocusOut}
                onKeyDown={handleKeyDownOnNameField}
              />
          }
          <button type="submit" className="button-main" disabled={isSystemMessageLoading}>
            {
              isMobile ? <PaperAirplaneIcon className="w-5"/> : <span>{t("LABEL.SEND")}</span>
            }
          </button>

        </form>
      </div>


    </div>
    <div className="backdrop-blur-sm bg-background/50 fixed bottom-0 left-4 right-4 h-[70px] collapse sm:visible" /></>
}




const ShareButton = () => {

  const sessionId = useSelector(state => state.chatState.sessionInfo!.sessionId)
  const urlOrigin = useMemo(() => new URL(window.location.href).origin, [])
  const shareURL = useMemo(() => {
    return path.join(urlOrigin, "share", sessionId)
  }, [urlOrigin, sessionId])

  const [t] = useTranslation()

  const onCopy = useCallback((text: string, result: boolean) => {
    enqueueSnackbar(t("CHAT.LINK_COPIED"), {
      autoHideDuration: 1000,
      preventDuplicate: true
    })
  }, [t])

  return <CopyToClipboard text={shareURL} onCopy={onCopy}>
    <button className="button-clear button-tiny button-with-icon opacity-70">
      <ClipboardDocumentIcon className="w-4 mr-1 opacity-70" />
      <span>{t("CHAT.SHARE_LINK")}</span>
    </button></CopyToClipboard>
}

const SessionMessageView = (props: { id: EntityId, isLast: boolean }) => {

  const dispatch = useDispatch()

  const userName = useSelector(state => state.chatState.sessionInfo?.name!)

  const turn = useSelector(state => state.chatState.messages.entities[props.id]!)
  const isEmotionSelectionTurn = turn.metadata?.select_emotion === true

  const emotionSelectionResult = useSelector(state => {
    const turn = state.chatState.messages.entities[props.id]!
    const isEmotionSelectionTurn = turn.metadata?.select_emotion === true
    if(!props.isLast && turn.is_user === false && isEmotionSelectionTurn === true){
      const index = state.chatState.messages.ids.indexOf(turn.id)
      const resp = state.chatState.messages.entities[state.chatState.messages.ids[index+1]]
      if(resp?.is_user === true){
        const emotions = [...resp!.message.matchAll(/{key\:\s+\"([a-zA-Z]+)\"}/g)].map(arr => arr[1])
        return emotions.reduce((obj: any, emotion)=>{
          obj[emotion] = true
          return obj
        }, {})
      }else return undefined
    }else return undefined
  })

  const hideMessage = turn.metadata?.hide === true

  const isSystemBusy = useSelector(state => state.chatState.isLoadingMessage)

  const [t] = useTranslation()

  const onDoubleClick = useCallback(()=>{
    if(turn.is_user === false && props.isLast === true){
      if(confirm(t("CHAT.CONFIRM_REGEN_LAST_MESSAGE"))){
        dispatch(regenerateLastSystemMessage())
      }
    }
  }, [turn.is_user, props.isLast, t])

  return hideMessage ? null : <MessageView avatarHash={turn.is_user === true ? userName : "system"} message={turn} onThumbnailDoubleClick={onDoubleClick} componentsBelowCallout={
      !isEmotionSelectionTurn
        ? null : <>
          <EmotionPicker messageId={props.id} disabled={!props.isLast || isSystemBusy === true} value={emotionSelectionResult}/>
        </>
    }/>
}
