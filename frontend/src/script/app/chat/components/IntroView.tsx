import * as yup from "yup"
import {useForm} from "react-hook-form";
import {yupResolver} from "@hookform/resolvers/yup";
import {KeyboardEvent, useCallback, useEffect} from "react";
import {useDispatch} from "../../../redux/hooks";
import {initializeChatSession} from "../reducer";
import { IntroFormFrame } from "./IntroFormFrame";
import { useTranslation } from "react-i18next";
import { LanguageSelector } from "./LanguageSelector";

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


    const [t, i18n] = useTranslation()

    const onSubmit = useCallback((data: {user_name: string, user_age: number}) => {
        dispatch(initializeChatSession(props.sessionId, data.user_name, data.user_age, i18n.language))
    }, [props.sessionId, i18n])

    useEffect(()=>{
        setFocus("user_name")
    }, [setFocus])

    const handleKeyDownOnNameField = useCallback((ev: KeyboardEvent<HTMLInputElement>)=>{
        if(ev.key == 'Enter'){
            ev.preventDefault()
            if(!getFieldState("user_name").invalid){
                setFocus("user_age")
            }
        }
    }, [getFieldState, setFocus])

    return <IntroFormFrame>
        <div className="panel">
            <LanguageSelector className="self-end mb-2"/>
            <form onSubmit={handleSubmit(onSubmit)}>
        <input {...register("user_name")} type="text" placeholder={t("SIGN_IN.USER_NAME_PLACEHOLDER")} 
        autoComplete="off"
        className=""
        onKeyDown={handleKeyDownOnNameField}
        />

        <input {...register("user_age")} type="number" placeholder={t("SIGN_IN.USER_AGE_PLACEHOLDER")} className="mt-2" autoComplete="off"/>
        {
            isValid ? <input type={"submit"} value={t("SIGN_IN.START")} className="button-main mt-2"/> : undefined
        }
        
    </form>
        </div>
        </IntroFormFrame>
}