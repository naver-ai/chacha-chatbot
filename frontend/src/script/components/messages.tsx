import { ChatMessage } from "../types"
import Avatar from "boring-avatars"
import {useSelector} from "../redux/hooks";

export const MessageView = (props: {
    avatarHash: string,
    message: ChatMessage,
    overrideMessageText?: string, 
    children?: any,
    hideCallout?: boolean,
    componentsAboveCallout?: any,
    componentsBelowCallout?: any,
    onThumbnailDoubleClick?: () => void
}) => {

    return <div className={`turn-container ${props.message.is_user ? "user" : "system"}`}>
        <div className="profilePic" id = {!props.message.is_user ? "systemPic" : ""} onDoubleClick={props.onThumbnailDoubleClick}>
            <Avatar
                size={40}
                name= {props.avatarHash}
                variant="beam"
                colors={["#A8D1D1","#F1F7B5", "#9EA1D4", "#6495ED"]}
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