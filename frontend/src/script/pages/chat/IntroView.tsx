import * as yup from "yup"
import {useForm} from "react-hook-form";
import {yupResolver} from "@hookform/resolvers/yup";
import {useCallback} from "react";
import {useDispatch} from "../../redux/hooks";
import {initializeChatSession} from "./reducer";

const schema = yup.object({
    user_name: yup.string().required(),
    user_age: yup.number().required().integer().positive()
}).required()

export const IntroView = (props: {
    sessionId: string
}) => {
    const {
        register,
        handleSubmit,
        formState: {errors}
    } = useForm({
        resolver: yupResolver(schema)
    })

    const dispatch = useDispatch()

    const onSubmit = useCallback((data: {user_name: string, user_age: number}) => {
        dispatch(initializeChatSession(props.sessionId, data.user_name, data.user_age))
    }, [props.sessionId])

    return <form onSubmit={handleSubmit(onSubmit)}>
        <input {...register("user_name")} placeholder={"너의 이름은 뭐야? (성 빼고)"}/>
        <p>{errors.user_name?.message}</p>

        <input {...register("user_age")} placeholder={"몇살이야?"}/>
        <p>{errors.user_age?.message}</p>

        <input type={"submit"} value={"대화 시작하기"}/>
    </form>
}