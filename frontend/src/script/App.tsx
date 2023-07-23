import {BrowserRouter, Navigate, Route, Routes} from "react-router-dom";
import {ChatPage} from "./pages/chat";
import {store} from "./redux/store";
import {Provider} from "react-redux";
import { ChatSharePage } from "./pages/chat-share";
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