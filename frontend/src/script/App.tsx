import {BrowserRouter, Navigate, Route, Routes} from "react-router-dom";
import {ChatPage} from "./pages/chat";
import {store} from "./redux/store";
import {Provider} from "react-redux";


export function App() {
    return <Provider store={store}><BrowserRouter>
        <Routes>
            <Route index element={<Navigate to={"chat"}/>}/>
            <Route path={"/chat"} element={<ChatPage/>}/>
        </Routes>
    </BrowserRouter></Provider>
}