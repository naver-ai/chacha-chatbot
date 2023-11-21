import { AppDispatch, ReduxAppState } from "../../redux/store";
import {ChatMessage} from "../../types";
import {createEntityAdapter, createSlice, Draft, EntityAdapter, PayloadAction} from "@reduxjs/toolkit";
import { NetworkHelper } from "../../network";
import i18n from "src/i18n";


const messagesAdapter = createEntityAdapter<ChatMessage>()

const INITIAL_MESSAGES_STATE = messagesAdapter.getInitialState()

export interface ChatState{
    sessionInfo?: {
        sessionId: string,
        name: string,
        age: number,
        locale: string
    } | undefined

    isLoadingMessage: boolean

    messages: typeof INITIAL_MESSAGES_STATE
}

const INITIAL_CHAT_STATE: ChatState = {
    sessionInfo: undefined,
    isLoadingMessage: false,
    messages: INITIAL_MESSAGES_STATE
}

const chatSlice = createSlice({
    name: "chat",
    initialState: INITIAL_CHAT_STATE,
    reducers: {
        init: (state) => {
            return INITIAL_CHAT_STATE
        },

        initialize_session_info: (state, action: PayloadAction<{
            userName: string, userAge: number, sessionId: string, locale: string}>) => {
            state.sessionInfo = {
                name: action.payload.userName,
                age: action.payload.userAge,
                locale: action.payload.locale,
                sessionId: action.payload.sessionId
            }
            messagesAdapter.removeAll(state.messages)
        },

        setLoadingState: (state, action: PayloadAction<boolean>) => {
            state.isLoadingMessage = action.payload
        },

        addMessage: (state, action) => {
            messagesAdapter.addOne(state.messages, action)
        },

        removeMessage: (state, action) => {
            messagesAdapter.removeOne(state.messages, action)
        },

        setMessages: (state, action) => {
            messagesAdapter.removeAll(state.messages)
            messagesAdapter.addMany(state.messages, action)
        },
    }
})


export function loadChatSession(sessionId: string, autoReloadSystemMessage: boolean = false): (dispatch: AppDispatch, getState: () => ReduxAppState) => void {
    return async (dispatch: AppDispatch) => {
        dispatch(chatSlice.actions.setLoadingState(true))
        
        const [messages, info] = await Promise.all([NetworkHelper.loadSessionChatMessages(sessionId), NetworkHelper.loadSessionInfo(sessionId)])
        
        i18n.changeLanguage(info.locale)

        dispatch(chatSlice.actions.setLoadingState(false))
        dispatch(chatSlice.actions.initialize_session_info({ sessionId, userAge: info.user_age, userName: info.user_name, locale: info.locale}))
        dispatch(chatSlice.actions.setMessages(messages))

        if(autoReloadSystemMessage === true){
            if(messages.length > 0 && messages[messages.length - 1].is_user === true){
                // the last message is a user message
                console.log("Should process the user message.")
                const lastMessage = messages[messages.length - 1]
                requestAnimationFrame(()=>{
                    dispatch(chatSlice.actions.setLoadingState(true))
                    dispatch(chatSlice.actions.removeMessage(lastMessage.id))
                    NetworkHelper.sendUserMessage(sessionId, lastMessage).then(agentResponse => {
                        dispatch(chatSlice.actions.setLoadingState(false))
                        dispatch(chatSlice.actions.addMessage(agentResponse))
                    })
                })
            }
        }
    }
}


export function initializeChatSession(sessionId: string, 
    userName: string, userAge: number, locale: string): (dispatch: AppDispatch, getState: () => ReduxAppState) => void {
    return async (dispatch: AppDispatch) => {
        i18n.changeLanguage(locale)
        dispatch(chatSlice.actions.initialize_session_info({userName, userAge, sessionId, locale}))
        dispatch(chatSlice.actions.setLoadingState(true))
        const agentResponse = await NetworkHelper.initializeSession(sessionId, userName, userAge, locale)
        dispatch(chatSlice.actions.setLoadingState(false))
        dispatch(chatSlice.actions.addMessage(agentResponse))
    }
}


export function sendUserMessage(message: ChatMessage): (dispatch: AppDispatch, getState: () => ReduxAppState) => void {
    return async (dispatch: AppDispatch, getState: ()=>ReduxAppState) => {
        const sessionId = getState().chatState.sessionInfo?.sessionId
        if(sessionId != null){
            dispatch(chatSlice.actions.addMessage(message))
            dispatch(chatSlice.actions.setLoadingState(true))
            const agentResponse = await NetworkHelper.sendUserMessage(sessionId, message)
            dispatch(chatSlice.actions.setLoadingState(false))
            dispatch(chatSlice.actions.addMessage(agentResponse))
        }
    }
}


export function regenerateLastSystemMessage(): (dispatch: AppDispatch, getState: () => ReduxAppState) => void {
    return async (dispatch: AppDispatch, getState: ()=>ReduxAppState) => {
        const chatState = getState().chatState
        const sessionId = chatState.sessionInfo?.sessionId
        const lastMessage = getLastSystemMessage(chatState.messages)
        if(sessionId != null && lastMessage != null && lastMessage.is_user == false){
            dispatch(chatSlice.actions.removeMessage(lastMessage.id))
            dispatch(chatSlice.actions.setLoadingState(true))
            const agentResponse = await NetworkHelper.regenerateLastSystemMessage(sessionId)
            dispatch(chatSlice.actions.setLoadingState(false))
            dispatch(chatSlice.actions.addMessage(agentResponse))
        }
    }
}


function getLastSystemMessage(messagesState: typeof INITIAL_MESSAGES_STATE): ChatMessage | null{
    const numMessages = messagesState.ids.length
    if(numMessages > 0){
        return messagesState.entities[messagesState.ids[messagesState.ids.length - 1]]!
    }else return null
}

export const { init } = chatSlice.actions

export default chatSlice.reducer