import {combineReducers, configureStore} from "@reduxjs/toolkit";
import chatReducer from '../pages/chat/reducer'
import chatShareReducer from '../pages/chat-share/reducer'

const rootReducer = combineReducers({
    chatState: chatReducer,
    chatShareState: chatShareReducer
})

const store = configureStore({
    reducer: rootReducer
})

export {store}

export type ReduxAppState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch