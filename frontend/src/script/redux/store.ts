import {combineReducers, configureStore} from "@reduxjs/toolkit";
import chatReducer from '../app/chat/reducer'
import chatShareReducer from '../app/chat-share/reducer'

const rootReducer = combineReducers({
    chatState: chatReducer
})

const store = configureStore({
    reducer: rootReducer
})

export {store}

export type ReduxAppState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch