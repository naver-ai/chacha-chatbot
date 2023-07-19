import { AppDispatch, ReduxAppState } from "../../redux/store";
import {ChatMessage} from "../../types";
import {createEntityAdapter, createSlice, Draft, PayloadAction} from "@reduxjs/toolkit";
import { NetworkHelper } from "../../network";

const messagesAdapter = createEntityAdapter<ChatMessage>()

const INITIAL_MESSAGES_STATE = messagesAdapter.getInitialState()

export interface ChatState{
    sessionInfo?: {
        sessionId: string,
        name: string,
        age: number
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
        initialize: (state, action: PayloadAction<{
            userName: string, userAge: number, sessionId: string}>) => {
            state.sessionInfo = {
                name: action.payload.userName,
                age: action.payload.userAge,
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
    }
})

export function initializeChatSession(sessionId: string, userName: string, userAge: number): (dispatch: AppDispatch, getState: () => ReduxAppState) => void {
    return async (dispatch: AppDispatch) => {
        dispatch(chatSlice.actions.initialize({userName, userAge, sessionId}))
        dispatch(chatSlice.actions.setLoadingState(true))
        const agentResponse = await NetworkHelper.initializeSession(sessionId, userName, userAge)
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

export default chatSlice.reducer