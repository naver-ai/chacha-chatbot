import { ChatMessage } from "../types"
import Avatar from "boring-avatars"
import { TypeAnimation } from 'react-type-animation';

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
        {
            props.message.is_user === true ? null : <div className="profilePic" id = {!props.message.is_user ? "systemPic" : ""} onDoubleClick={props.onThumbnailDoubleClick}>
            <Avatar
                size={40}
                name= {props.avatarHash}
                variant="beam"
                colors={["#A8D1D1","#F1F7B5", "#9EA1D4", "#6495ED"]}
            />
        </div>
        }
        <div>
            {
                props.componentsAboveCallout
            }
            {
                props.hideCallout === true ? null : props.message.is_user === true ? <div className="callout" dangerouslySetInnerHTML={{ __html: props.overrideMessageText || props.message.message }}/> 
                : <div className="callout">
                    <TypeAnimation sequence={[props.overrideMessageText || props.message.message]} speed={70} cursor={false}/>
                    </div>
            }
            {
                props.componentsBelowCallout
            }
        </div>

    </div>
  }