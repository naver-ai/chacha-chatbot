import { yupResolver } from "@hookform/resolvers/yup";
import { EntityId, nanoid } from "@reduxjs/toolkit"
import { useCallback } from "react";
import { useForm } from "react-hook-form";
import * as yup from 'yup';
import { sendUserMessage } from "../reducer";
import { useDispatch } from "src/script/redux/hooks";

const EMOTION_LIST = [
    { "key": "joy", "label": "기쁨 😃" },
    { "key": "trust", "label": "신뢰 🤝" },
    { "key": "surprise", "label": "놀람 😮" },
    { "key": "anticipation", "label": "기대 🤔" },
    { "key": "fear", "label": "두려움 😨" },
    { "key": "sadness", "label": "슬픔 😢" },
    { "key": "disgust", "label": "불쾌함 🤮" },
    { "key": "anger", "label": "화남 😠" },
    { "key": "optimism", "label": "낙관 😄" },
    { "key": "love", "label": "사랑 😍" },
    { "key": "submission", "label": "굴복감 😔" },
    { "key": "awe", "label": "경외감 😲" },
    { "key": "disapproval", "label": "못마땅함 😒" },
    { "key": "remorse", "label": "후회 😞" },
    { "key": "contempt", "label": "경멸 😏" },
    { "key": "aggressiveness", "label": "공격성 😡" }
]

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
                const id = props.messageId + "_" + em.key
                return <span className="emotion" key={em.key}>
                    <input type="checkbox" disabled={props.disabled} id={id} {...register(`emotions.${em.key}` as any)} />
                    <label htmlFor={id}>{em.label}</label>
                </span>
            })
        }
        {
            (isValid === true && props.disabled !== true) ? <input id="submitEmotion" type="submit" value="보내기" className="button-main" /> : null
        }        
    </form>
}