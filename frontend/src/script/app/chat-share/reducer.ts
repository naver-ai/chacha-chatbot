import { AppDispatch, ReduxAppState } from "../../redux/store";
import {ChatMessage} from "../../types";
import {createEntityAdapter, createSlice, Draft, PayloadAction} from "@reduxjs/toolkit";
import { NetworkHelper } from "../../network";

const messagesAdapter = createEntityAdapter<ChatMessage>()

const INITIAL_MESSAGES_STATE = messagesAdapter.getInitialState()

export interface ChatShareState{
    sessionId: string | undefined
    isLoading: boolean
    userName: string | undefined,
    userAge: number | undefined,
    messages: typeof INITIAL_MESSAGES_STATE
}

const INITIAL_CHAT_STATE: ChatShareState = {
    sessionId: undefined,
    isLoading: false,
    userName: undefined,
    userAge: undefined,
    messages: INITIAL_MESSAGES_STATE
}

const chatSlice = createSlice({
    name: "chat-share",
    initialState: INITIAL_CHAT_STATE,
    reducers: {
        initialize: (state, action: PayloadAction<string>) => {
            state.sessionId = action.payload
            messagesAdapter.removeAll(state.messages)
        },

        setUserInfo: (state, action: PayloadAction<{userName: string, userAge: number}>) => {
            state.userAge = action.payload.userAge
            state.userName = action.payload.userName
        },

        setLoadingState: (state, action: PayloadAction<boolean>) => {
            state.isLoading = action.payload
        },

        setMessages: (state, action) => {
            messagesAdapter.removeAll(state.messages)
            messagesAdapter.addMany(state.messages, action)
        },
    }
})

export function loadChatSession(sessionId: string): (dispatch: AppDispatch, getState: () => ReduxAppState) => void {
    return async (dispatch: AppDispatch) => {
        dispatch(chatSlice.actions.initialize(sessionId))
        dispatch(chatSlice.actions.setLoadingState(true))
        
        const [messages, info] = await Promise.all([NetworkHelper.loadSessionChatMessages(sessionId), NetworkHelper.loadSessionInfo(sessionId)])
        
        dispatch(chatSlice.actions.setLoadingState(false))
        dispatch(chatSlice.actions.setMessages(messages))
        dispatch(chatSlice.actions.setUserInfo({userAge: info.user_age, userName: info.user_name}))
    }
}

export default chatSlice.reducer