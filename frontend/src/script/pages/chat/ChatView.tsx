import { yupResolver } from "@hookform/resolvers/yup"
import { EntityId, nanoid } from "@reduxjs/toolkit"
import { useCallback, useEffect, useRef } from "react"
import { useForm } from "react-hook-form"
import { useDispatch, useSelector } from "src/script/redux/hooks"
import * as yup from "yup"
import { sendUserMessage } from "./reducer"
import { useDebounceCallback } from '@react-hook/debounce'

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

    useEffect(()=>{
        requestAnimationFrame(()=>{
            scrollToBottom()
        })
    }, [messageIds.length])

    return <div className="turn-list-container overflow-y-auto" ref={scrollViewRef}>
        <div className="turn-list container mx-auto px-10">{
            messageIds.map(id => {
                return <MessageView key={id.toString()} id={id}/>
            })
        }</div>
        <TypingPanel/>
    </div>
}


const schema = yup.object({
    message: yup.string().required()
}).required()

const TypingPanel = ()=>{

    const isSystemMessageLoading = useSelector(state => state.chatState.isLoadingMessage)

    const dispatch = useDispatch()

    const {
        register,
        handleSubmit,
        reset,
        setFocus,
        formState: {errors, isValid},
    } = useForm({
        resolver: yupResolver(schema),
        reValidateMode: 'onChange'
    })

    const onSubmit = useCallback((data: {message: string}) => {
        if(!isSystemMessageLoading){
            reset({message: ""})
            dispatch(sendUserMessage({id: nanoid(), message: data.message, is_user: true, metadata: undefined, timestamp: Date.now()}))
        }
    }, [isSystemMessageLoading])

    useEffect(()=>{
        setFocus('message')
    }, [setFocus])

    return <><div id="chat-typing-panel" className="fixed z-10 left-4 right-4 bottom-10 lg:left-0 lg:right-0">
        <form onSubmit={handleSubmit(onSubmit)} className="container flex flex-row bg-slate-50 px-3 py-1.5 pl-1.5 rounded-lg shadow-lg relative">
        {
            isSystemMessageLoading ? <div className="text-input text-chat-1 animate-pulse-fast flex-1 mr-2">할 말을 생각 중이야. 잠시만 기다려줘!</div> : 
            <input {...register("message")} type="text" autoFocus={true} placeholder={"나에게 할 말을 입력해줘!"}
        className="flex-1 mr-2"
        autoComplete="off"
        />
        }
        <input type="submit" value="보내기" className="button-main" disabled={isSystemMessageLoading}/>
    </form>
    </div>
    <div className="bg-background/70 fixed bottom-0 left-10 right-10 h-[50px]"/></>
}

const MessageView = (props: {id: EntityId}) => {
    const turn = useSelector(state => state.chatState.messages.entities[props.id]!)

    return <div className={`turn-container ${turn.is_user ? "user" : "system"}`}>
            <div className="callout" dangerouslySetInnerHTML={{__html: turn.message}}></div>
        </div>
}