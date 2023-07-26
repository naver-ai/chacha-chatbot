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
import Avatar from "boring-avatars";

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

  const lastSystemMessageText = useSelector(state => {
    const lastSystemMessageId = state.chatState.messages.ids.findLast(id => state.chatState.messages.entities[id]?.is_user === false)
    if(lastSystemMessageId){
      return state.chatState.messages.entities[lastSystemMessageId]?.message
    }else{
      return undefined
    }
  })

  const shouldHideTypingPanel = useMemo(()=>{
    return lastSystemMessageText?.includes("<|EmotionSelect|>")
  }, [lastSystemMessageText])

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

  return shouldHideTypingPanel ? null : <>
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

  const message = useMemo(()=>{
    if(turn.message.includes("<|EmotionSelect|>")){
      return turn.message.replace("<|EmotionSelect|>", "")
    }else return turn.message
  }, [turn.message])

  const isEmotionSelectionTurn = useMemo(()=>{
    return turn.is_user === false && turn.message.includes("<|EmotionSelect|>")
  }, [turn.message, turn.is_user])

  return <MessageView message={turn} overrideMessageText={message}>
    {
      !isEmotionSelectionTurn 
      ? null : <>
        <form class="emolist">
          <span class="emotions">
            <input type="checkbox" id="joy"/>
            <label for="joy">기쁨 😃</label>
          </span>
          <span class="emotions">
            <input type="checkbox" id="trust"/>
            <label class="emotions" for="trust">신뢰 🤝 </label>
          </span>
          <span class="emotions">
            <input type="checkbox" id="surprise"/>
            <label for="surprise">놀람 😮</label>
          </span>
          <span class="emotions">
            <input type="checkbox" id="anticipation"/>
            <label class="emotions" for="anticipation">기대 🤔</label>
          </span>
          <span class="emotions">
            <input type="checkbox" id="fear"/>
            <label for="fear">두려움 😨</label>
          </span>
          <span class="emotions">
            <input type="checkbox" id="sadness"/>
            <label class="emotions" for="Sadness">슬픔 😢</label>
          </span>
          <span class="emotions">
            <input type="checkbox" id="disgust"/>
            <label for="disgust">불쾌함 🤮</label>
          </span>
          <span class="emotions">
            <input type="checkbox" id="anger"/>
            <label class="emotions" for="anger">화남 😠</label>
          </span>
          <span class="emotions">
            <input type="checkbox" id="optimism"/>
            <label for="optimism">낙관 😄</label>
          </span>
          <span class="emotions">
            <input type="checkbox" id="love"/>
            <label class="emotions" for="love">사랑 😍</label>
          </span>
          <span class="emotions">
            <input type="checkbox" id="submission"/>
            <label for="submission">굴복감 😔</label>
          </span>
          <span class="emotions">
            <input type="checkbox" id="awe"/>
            <label class="emotions" for="awe">경외감 😲</label>
          </span>
          <span class="emotions">
            <input type="checkbox" id="disapproval"/>
            <label class="emotions" for="disapproval">못마땅함 😒</label>
          </span>
          <span class="emotions">
            <input type="checkbox" id="remorse"/>
            <label for="remorse">후회 😞</label>
          </span>
          <span class="emotions">
            <input type="checkbox" id="contempt"/>
            <label class="emotions" for="contempt">경멸 😏</label>
          </span>
          <span class="emotions">
            <input type="checkbox" id="aggressiveness"/>
            <label for="aggressiveness">공격성 😡</label>
          </span>
          <input id="submitEmotion" type="submit" value="보내기" className="button-main"/>
        </form></>
    }
  </MessageView>
}
