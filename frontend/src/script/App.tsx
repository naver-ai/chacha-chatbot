import {BrowserRouter, Navigate, Route, Routes} from "react-router-dom";
import {ChatPage} from "./app/chat/pages/ChatPage";
import {store} from "./redux/store";
import {Provider} from "react-redux";
import { ChatSharePage } from "./app/chat/pages/ChatShare";
import {SnackbarProvider} from 'notistack';
import { SessionSignInPage } from "./app/chat/pages/SessionSignInPage";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { nanoid } from "nanoid";
import { format } from "date-fns";
import { init } from "./app/chat/reducer";

const generateDefaultSessionId = (): string => {
    const timestamp = format(new Date(), 'yyMMdd-HHmmss')
    const id = nanoid(5)
    return `${timestamp}-${id}`
}

const AutoRedirect = () => {
    const navigate = useNavigate();
    const dispatch = useDispatch();

    useEffect(() => {
        dispatch(init());
        const sessionId = generateDefaultSessionId();
        navigate(`/chat/${sessionId}`, { replace: true });
    }, [navigate, dispatch]);

    return null;
};

export function App() {
    return <Provider store={store}>
        <SnackbarProvider maxSnack={3}><BrowserRouter>
            <Routes>
                <Route index element={<AutoRedirect/>}/>
                <Route path={"/signin"} element={<SessionSignInPage/>}/>
                <Route path={"/chat/:sessionId"} element={<ChatPage/>}/>
                <Route path={"/share/:sessionId"} element={<ChatSharePage/>}/>
            </Routes>
        </BrowserRouter></SnackbarProvider>
    </Provider>
}