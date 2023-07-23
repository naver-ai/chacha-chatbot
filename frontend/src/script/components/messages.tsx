import { ChatMessage } from "../types"

export const MessageView = (props: { message: ChatMessage }) => {
    return <div className={`turn-container ${props.message.is_user ? "user" : "system"}`}>
      <div className="callout" dangerouslySetInnerHTML={{ __html: props.message.message }}></div>
    </div>
  }