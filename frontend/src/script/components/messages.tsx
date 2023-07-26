import { ChatMessage } from "../types"

export const MessageView = (props: { message: ChatMessage }) =>
    return <div className={`turn-container ${props.message.is_user ? "user" : "system"}`}>
        <img className="profilePic" id = {!props.message.is_user ? "systemPic" : ""} src=""/>
        <div>
            <div className="callout" dangerouslySetInnerHTML={{ __html: props.overrideMessageText || props.message.message }}></div>
            {
                props.children
            }
        </div>

    </div>
  }