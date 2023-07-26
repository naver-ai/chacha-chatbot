import { yupResolver } from "@hookform/resolvers/yup"
import { EntityId, nanoid } from "@reduxjs/toolkit"
import { useCallback, useEffect, useMemo, useRef } from "react"
import { useForm } from "react-hook-form"
import { useDispatch, useSelector } from "src/script/redux/hooks"
import * as yup from "yup"
import { sendUserMessage } from "./reducer"
import { MessageView } from "src/script/components/messages"
import {CopyToClipboard} from 'react-copy-to-clipboard';
import path from "path"
import {ClipboardDocumentIcon} from "@heroicons/react/20/solid";
import { enqueueSnackbar } from "notistack"
import {boolean} from "yup";

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

    return <div className="turn-list-container pt-10 overflow-y-auto justify-end h-full" ref={scrollViewRef}>
    <div className="turn-list container mx-auto px-10">{
       messageIds.map(id => {
        return <SessionMessageView key={id.toString()} id={id} />
      })
    }
    </div>
    <TypingPanel />
  </div>
}


const schema = yup.object({
  message: yup.string().required()
}).required()

const TypingPanel = () => {

  const isSystemMessageLoading = useSelector(state => state.chatState.isLoadingMessage)

  const dispatch = useDispatch()

  const {
    register,
    handleSubmit,
    reset,
    setFocus,
    formState: { errors, isValid },
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

  // const chatbotPic = document.getElementsByClassName("profilePic")[-1]
  // isSystemMessageLoading ? chatbotPic.addList.add("animate-pulse-fast") : chatbotPic.addList.add("")

  return <>
    <div id="chat-typing-panel" className="fixed z-10 left-4 right-4 bottom-10 lg:left-0 lg:right-0">
      <div className="container relative">
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-row bg-slate-50 px-3 py-1.5 pl-1.5 rounded-lg shadow-lg">
          {
            isSystemMessageLoading
                ? <div className="text-input text-chat-1 animate-pulse-fast flex-1 mr-2">할 말을 생각 중이야. 잠시만 기다려줘!</div>
                : <input {...register("message")} type="text" autoFocus={true} placeholder={"나에게 할 말을 입력해줘!"}
                       className="flex-1 mr-2"
                        autoComplete="off"
                        />
          }
          <input type="submit" value="보내기" className="button-main" disabled={isSystemMessageLoading} />
        
        </form>

        <div className="absolute bottom-2 left-0 translate-y-10">
            <ShareButton/>
          </div>
      </div>


    </div>
    <div className="bg-background/70 fixed bottom-0 left-10 right-10 h-[50px]" /></>
}




const ShareButton = () => {

  const sessionId = useSelector(state => state.chatState.sessionInfo!.sessionId)
  const urlOrigin = useMemo(() => new URL(window.location.href).origin, [])
  const shareURL = useMemo(()=> {
    return path.join(urlOrigin, "share", sessionId)
  }, [urlOrigin, sessionId])

  const onCopy = useCallback((text: string, result: boolean)=>{
    enqueueSnackbar('링크가 클립보드에 복사되었습니다.', {
      autoHideDuration: 1000,
      preventDuplicate: true
    })
  }, [])

  return <CopyToClipboard text={shareURL} onCopy={onCopy}>
    <button className="button-clear button-tiny button-with-icon opacity-70">
      <ClipboardDocumentIcon className="w-4 mr-1 opacity-70"/>
      <span>링크 공유하기</span>
    </button></CopyToClipboard>
}

const SessionMessageView = (props: { id: EntityId }) => {
  const turn = useSelector(state => state.chatState.messages.entities[props.id]!)
  return <MessageView message={turn}/>
}