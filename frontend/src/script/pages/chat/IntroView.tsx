import * as yup from "yup"
import {useForm} from "react-hook-form";
import {yupResolver} from "@hookform/resolvers/yup";
import {KeyboardEvent, useCallback, useEffect} from "react";
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
        setFocus,
        handleSubmit,
        formState: {errors, isValid},
        getFieldState
    } = useForm({
        resolver: yupResolver(schema),
        reValidateMode: 'onChange'
    })

    const dispatch = useDispatch()

    const onSubmit = useCallback((data: {user_name: string, user_age: number}) => {
        dispatch(initializeChatSession(props.sessionId, data.user_name, data.user_age))
    }, [props.sessionId])

    useEffect(()=>{
        setFocus("user_name")
    }, [setFocus])

    const handleKeyDownOnNameField = useCallback((ev: KeyboardEvent<HTMLInputElement>)=>{
        if(ev.key == 'Enter'){
            if(!getFieldState("user_name").invalid){
                setFocus("user_age")
            }
        }
    }, [getFieldState, setFocus])

    return <div className="flex flex-col justify-between h-screen">
        <div className="my-auto mx-auto chachaContainer">
            <div className="chachaTextBox">
                <span>ChaCha</span>
            </div>
            <img src=""/>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col container-sm my-auto mx-auto introViewChat">
        <input {...register("user_name")} type="text" placeholder={"너의 이름은 뭐야? (성 빼고)"} 
        autoComplete="off"
        className=""
        onKeyDown={handleKeyDownOnNameField}
        />

        <input {...register("user_age")} type="number" placeholder={"몇 살이야?"} className="mt-2" autoComplete="off"/>
        {
            isValid ? <input type={"submit"} value={"대화 시작하기!"} className="button-main mt-2"/> : undefined
        }
        
    </form></div>
}