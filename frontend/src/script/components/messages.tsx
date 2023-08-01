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
                colors={["#92A1C6", "#146A7C", "#F0AB3D", "#C271B4", "#C20D90"]}
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