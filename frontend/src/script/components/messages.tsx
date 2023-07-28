import { ChatMessage } from "../types"

export const MessageView = (props: { 
    message: ChatMessage, 
    overrideMessageText?: string, 
    children?: any,
    hideCallout?: boolean,
    componentsAboveCallout?: any,
    componentsBelowCallout?: any
}) => {
    return <div className={`turn-container ${props.message.is_user ? "user" : "system"}`}>
        <img className="profilePic" id = {!props.message.is_user ? "systemPic" : ""} src=""/>
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