import {BrowserRouter, Route, Routes} from "react-router-dom";
import {ChatPage} from "./app/chat/pages/ChatPage";
import {store} from "./redux/store";
import {Provider} from "react-redux";
import { ChatSharePage } from "./app/chat/pages/ChatShare";
import {SnackbarProvider} from 'notistack';
import { SessionSignInPage } from "./app/chat/pages/SessionSignInPage";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { nanoid } from "nanoid";
import { format } from "date-fns";
import { init } from "./app/chat/reducer";
import { useDispatch } from "./redux/hooks";
import {App as AntdApp, ConfigProvider, ThemeConfig} from "antd";

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

const theme: ThemeConfig = {
    token: {
        colorPrimary: '#6495ED',
        fontFamily: 'NanumSquareRound, -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
        fontSize: 16,
    },
}

export function App() {
    return <Provider store={store}>
                <SnackbarProvider maxSnack={3}>
                    <ConfigProvider theme={theme}>
                                <BrowserRouter>
                                    <Routes>
                                        <Route index element={<AutoRedirect/>}/>
                                        <Route path={"/chat/:sessionId"} element={<ChatPage/>}/>
                                        <Route path={"/share/:sessionId"} element={<ChatSharePage/>}/>
                                    </Routes>
                                </BrowserRouter>
                    </ConfigProvider>
                </SnackbarProvider>
    </Provider>
}