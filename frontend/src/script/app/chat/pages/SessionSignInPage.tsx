import { BackgroundPanel } from "src/script/components/background"
import { IntroFormFrame } from "../components/IntroFormFrame"
import * as yup from "yup"
import { useCallback, useEffect, useTransition } from "react"
import { useForm } from "react-hook-form"
import { yupResolver } from "@hookform/resolvers/yup"
import { useNavigate } from "react-router-dom"
import i18n, { LANGUAGE_LIST } from "src/i18n"
import { useTranslation } from "react-i18next"
import { LanguageSelector } from "../components/LanguageSelector"
import { useDispatch } from "react-redux"
import { init } from "../reducer"
import { nanoid } from "nanoid"
import { format } from "date-fns"


const schema = yup.object({
    sessionId: yup.string().matches(/^[a-zA-Z0-9\-_]+$/, i18n.t("SIGN_IN.ERROR.SESSION_ID")).trim().required()
}).required()

const generateDefaultSessionId = (): string => {
    const timestamp = format(new Date(), 'yyMMdd-HHmmss')
    const id = nanoid(5)
    return `${timestamp}-${id}`
}

export const SessionSignInPage = () => {

    const navigate = useNavigate();

    const {
        register,
        setFocus,
        setValue,
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

    const dispatch = useDispatch()
    
    useEffect(()=>{
        dispatch(init())
        setFocus('sessionId')
        setValue('sessionId', generateDefaultSessionId())
    }, [])

    return <>
    <IntroFormFrame>
        <div className="panel">
        {false && <LanguageSelector className="self-end mb-2"/>}
        <form onSubmit={handleSubmit(onSubmit)}>
            <label htmlFor="session_id" className="text-sm mb-0 ml-1 text-slate-400">세션 ID</label>
            <input id="session_id" {...register('sessionId')} type="text" placeholder={t("SIGN_IN.SESSION_NAME")} autoComplete="off"/>
            {
                errors.sessionId?.message != null ? <span className="text-sm mt-2 text-red-400">{errors.sessionId?.message}</span> : null
            }
            {
                isValid ? <input type={"submit"} value={t("LABEL.NEXT")} className="button-main mt-2"/> : undefined
            }
            
        </form>
        </div>
    </IntroFormFrame>
        <BackgroundPanel/>
    </>
}