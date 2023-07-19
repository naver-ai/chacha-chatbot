import { yupResolver } from "@hookform/resolvers/yup"
import { EntityId, nanoid } from "@reduxjs/toolkit"
import { useCallback } from "react"
import { useForm } from "react-hook-form"
import { useDispatch, useSelector } from "src/script/redux/hooks"
import * as yup from "yup"
import { sendUserMessage } from "./reducer"


export const ChatView = () => {
    
    const messageIds = useSelector(state => state.chatState.messages.ids)

    return <div>
        {
            messageIds.map(id => {
                return <MessageView key={id.toString()} id={id}/>
            })
        }
        <TypingPanel/>
    </div>
}


const schema = yup.object({
    message: yup.string().required(),
}).required()

const TypingPanel = ()=>{

    const dispatch = useDispatch()

    const {
        register,
        handleSubmit,
        reset,
        formState: {errors},
    } = useForm({
        resolver: yupResolver(schema)
    })

    const onSubmit = useCallback((data: {message: string}) => {
        reset({message: ""})
        dispatch(sendUserMessage({id: nanoid(), message: data.message, is_user: true, metadata: undefined, timestamp: Date.now()}))
    }, [])

    return <form onSubmit={handleSubmit(onSubmit)}>
        <input {...register("message")} autoFocus={true} placeholder={"나에게 할 말을 입력해줘!"}/>
        <input type="submit" value="보내기"/>
    </form>
}

const MessageView = (props: {id: EntityId}) => {
    const turn = useSelector(state => state.chatState.messages.entities[props.id]!)

    return <div dangerouslySetInnerHTML={{__html: turn.message}}></div>
}