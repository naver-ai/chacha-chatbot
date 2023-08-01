import { ChatMessage } from "../types"
import Avatar from "boring-avatars"
import {useSelector} from "../redux/hooks";

export const MessageView = (props: {
    message: ChatMessage, 
    overrideMessageText?: string, 
    children?: any,
    hideCallout?: boolean,
    componentsAboveCallout?: any,
    componentsBelowCallout?: any
}) => {
    const sessionInfo = useSelector(state => state.chatState.sessionInfo)
    return <div className={`turn-container ${props.message.is_user ? "user" : "system"}`}>
        <div className="profilePic" id = {!props.message.is_user ? "systemPic" : ""}>
            <Avatar
                size={40}
                name= {props.message.is_user ? sessionInfo?.name : "system"}
                variant="beam"
                colors={["#FD8A8A", "#F1F7B5", "#A8D1D1", "#9EA1D4", "#FAF3F0", "#D4E2D4", "#FFCACC", "#DBC4F0"]}
                className="avatars"
            />
        </div>
        <div>
            {
                props.componentsAboveCallout
            }
            {
                props.hideCallout === true ? null : <div className="callout" dangerouslySetInnerHTML={{ __html: props.overrideMessageText || props.message.message }}/>
            }
            {
                props.componentsBelowCallout
            }
        </div>

    </div>
  }