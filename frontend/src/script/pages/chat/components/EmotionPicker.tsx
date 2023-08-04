import { yupResolver } from "@hookform/resolvers/yup";
import { EntityId, nanoid } from "@reduxjs/toolkit"
import { useCallback } from "react";
import { useForm } from "react-hook-form";
import * as yup from 'yup';
import { sendUserMessage } from "../reducer";
import { useDispatch } from "src/script/redux/hooks";
import { EMOTION_LIST } from "src/script/concepts";

const schema = yup.object({
    emotions: yup.object().required()
    .test('contains-emotion-keys', "하나 이상의 감정을 선택해야 해!",
        (value: any, context) => {
            const keys = Object.keys(value)
            return keys.find(key => value[key] === true) != null
        })
}) 

export const EmotionPicker = (props: { messageId: EntityId, disabled?: boolean }) => {

    const dispatch = useDispatch()

    const { register, handleSubmit, formState: {errors, isValid} } = useForm({
        resolver: yupResolver(schema),
        mode: 'onChange',
        reValidateMode: 'onChange'
    })

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

    return <form className="emolist" onSubmit={handleSubmit(onSubmit)} aria-disabled={props.disabled}>
        {
            EMOTION_LIST.map(em => {
                const id = props.messageId + "_" + em.en
                return <span className="emotion" key={em.en}>
                    <input type="checkbox" disabled={props.disabled} id={id} {...register(`emotions.${em.en}` as any)} />
                    <label htmlFor={id}>{em.kr} {em.emoji}</label>
                </span>
            })
        }
        {
            (isValid === true && props.disabled !== true) ? <input id="submitEmotion" type="submit" value="보내기" className="button-main" /> : null
        }        
    </form>
}