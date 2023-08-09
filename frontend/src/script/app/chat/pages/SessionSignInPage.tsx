import { BackgroundPanel } from "src/script/components/background"
import { IntroFormFrame } from "../components/IntroFormFrame"
import * as yup from "yup"
import { useCallback, useEffect } from "react"
import { useForm } from "react-hook-form"
import { yupResolver } from "@hookform/resolvers/yup"
import { useNavigate } from "react-router-dom"


const schema = yup.object({
    sessionId: yup.string().matches(/^[a-zA-Z0-9\-_]+$/, "세션 아이디는 공백 없는 대소문자와 숫자, 하이픈, 언더바만 가능해.").trim().required()
}).required()

export const SessionSignInPage = () => {

    const navigate = useNavigate();

    const {
        register,
        setFocus,
        handleSubmit,
        formState: {errors, isValid},
    } = useForm({
        resolver: yupResolver(schema),
        reValidateMode: 'onChange'
    })

    const onSubmit = useCallback(async (data: {sessionId: string}) => {
        navigate(`/chat/${data.sessionId}`)
    }, [])
    
    useEffect(()=>{
        setFocus('sessionId')
    }, [])

    return <>
    <IntroFormFrame>

        <form onSubmit={handleSubmit(onSubmit)}>

            <input {...register('sessionId')} type="text" placeholder={"세션 이름"} autoComplete="off"/>
            {
                errors.sessionId?.message != null ? <span className="text-sm mt-2 text-red-400">{errors.sessionId?.message}</span> : null
            }
            {
                isValid ? <input type={"submit"} value={"다음"} className="button-main mt-2"/> : undefined
            }
            
        </form>
    </IntroFormFrame>
        <BackgroundPanel/>
    </>
}