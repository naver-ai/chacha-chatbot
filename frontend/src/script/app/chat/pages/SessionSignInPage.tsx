import { BackgroundPanel } from "src/script/components/background"
import { IntroFormFrame } from "../components/IntroFormFrame"
import * as yup from "yup"
import { useCallback, useEffect, useTransition } from "react"
import { useForm } from "react-hook-form"
import { yupResolver } from "@hookform/resolvers/yup"
import { useNavigate } from "react-router-dom"
import i18n from "src/i18n"
import { useTranslation } from "react-i18next"


const schema = yup.object({
    sessionId: yup.string().matches(/^[a-zA-Z0-9\-_]+$/, i18n.t("SIGN_IN.ERROR.SESSION_ID")).trim().required()
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

    const [t] = useTranslation()
    
    useEffect(()=>{
        setFocus('sessionId')
    }, [])

    return <>
    <IntroFormFrame>

        <form onSubmit={handleSubmit(onSubmit)}>

            <input {...register('sessionId')} type="text" placeholder={t("SIGN_IN.SESSION_NAME")} autoComplete="off"/>
            {
                errors.sessionId?.message != null ? <span className="text-sm mt-2 text-red-400">{errors.sessionId?.message}</span> : null
            }
            {
                isValid ? <input type={"submit"} value={t("LABEL.NEXT")} className="button-main mt-2"/> : undefined
            }
            
        </form>
    </IntroFormFrame>
        <BackgroundPanel/>
    </>
}