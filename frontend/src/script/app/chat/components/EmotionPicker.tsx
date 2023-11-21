import { yupResolver } from "@hookform/resolvers/yup";
import { EntityId, nanoid } from "@reduxjs/toolkit"
import { useCallback, useEffect } from "react";
import { useForm } from "react-hook-form";
import * as yup from 'yup';
import { sendUserMessage } from "../reducer";
import { useDispatch } from "src/script/redux/hooks";
import { EMOTION_LIST } from "src/script/concepts";
import i18n from "src/i18n";
import { useTranslation } from "react-i18next";

const schema = yup.object({
    emotions: yup.object().required()
    .test('contains-emotion-keys', i18n.t("EMOTION_PICKER.ERROR.NOTHING_SELECTED"),
        (value: any, context) => {
            const keys = Object.keys(value)
            return keys.find(key => value[key] === true) != null
        })
}) 

export const EmotionPicker = (props: { messageId: EntityId, disabled?: boolean, value?: {[key:string]: boolean} }) => {

    const dispatch = useDispatch()

    const { register, handleSubmit, formState: {errors, isValid}, reset } = useForm({
        resolver: yupResolver(schema),
        mode: 'onChange',
        reValidateMode: 'onChange'
    })

    useEffect(()=>{
        if(props.value != null){
            reset({emotions: props.value})
        }
    }, [props.value])

    const onSubmit = useCallback((data: {emotions: {[key:string]: boolean}})=>{
        const selectedEmotions = Object.keys(data.emotions).filter(key => data.emotions[key] === true)
        dispatch(sendUserMessage({
            id: nanoid(),
            message: selectedEmotions.map(e => `{key: "${e}"}`).join(", "),
            is_user: true,
            metadata: {
                hide: true,
                selected_emotions: selectedEmotions,
            },
            timestamp: Date.now()
        }))
    }, [])

    const [t, i18n] = useTranslation()

    return <form className="emolist" onSubmit={handleSubmit(onSubmit)} aria-disabled={props.disabled}>
        {
            EMOTION_LIST.map(em => {
                const id = props.messageId + "_" + em.en
                return <span className="emotion" key={em.en}>
                    <input type="checkbox" disabled={props.disabled} id={id} {...register(`emotions.${em.en}` as any)} />
                    <label htmlFor={id}>{i18n.language == 'kr' ? em.kr : em.en} {em.emoji}</label>
                </span>
            })
        }
        {
            (isValid === true && props.disabled !== true) ? <input id="submitEmotion" type="submit" value={t("LABEL.SEND")} className="button-main" /> : null
        }        
    </form>
}