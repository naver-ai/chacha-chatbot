import {BrowserRouter, Navigate, Route, Routes} from "react-router-dom";
import {ChatPage} from "./app/chat/pages/ChatPage";
import {store} from "./redux/store";
import {Provider} from "react-redux";
import { ChatSharePage } from "./app/chat/pages/ChatShare";
import {SnackbarProvider} from 'notistack';

export function App() {
    return <Provider store={store}>
        <SnackbarProvider maxSnack={3}><BrowserRouter>
        <Routes>
            <Route index element={<Navigate to={"chat"}/>}/>
            <Route path={"/chat"} element={<ChatPage/>}/>
            <Route path={"/share/:sessionId"} element={<ChatSharePage/>}/>
        </Routes>
    </BrowserRouter></SnackbarProvider></Provider>
}