import {IntroView} from "./IntroView";
import {useEffect, useRef, useState} from "react";
import {nanoid} from "nanoid";
import {useSelector} from "../../redux/hooks";
import {ChatView} from "./ChatView";

export const ChatPage = ()=>{

    const [sessionId, setSessionId] = useState<string|undefined>(undefined)

    useEffect(()=>{
        setSessionId(nanoid())
    }, [])

    const isInitialized = useSelector(state => state.chatState.sessionInfo != null)


    return <div className="App h-screen flex flex-col justify-between">
        {
            isInitialized ? <ChatView/> : <IntroView sessionId={sessionId!!}/>
        }
        <div className="background-panel fixed top-0 left-0 right-0 bottom-0 z-[-1] pointer-events-none"/>
    </div>
}