import * as i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const kr = {
    SIGN_IN: {
        ERROR:{
            SESSION_ID: "세션 아이디는 공백 없는 대소문자와 숫자, 하이픈, 언더바만 가능해."
        },
        SESSION_NAME: "세션 이름",
        USER_NAME_PLACEHOLDER: "너의 이름은 뭐야? (성 빼고)",
        USER_AGE_PLACEHOLDER: "몇 살이야?",
        START: "대화 시작하기!"
    },
    SHARE: {
        SAVE: "CSV로 저장"
    },
    CHAT: {
        PROCESSING: "할 말을 생각 중이야. 잠시만 기다려줘!",
        INPUT_PLACEHOLDER: "나에게 할 말을 입력해줘!",
        SHARE_LINK: "링크 공유하기",
        LINK_COPIED: "링크가 클립보드에 복사되었습니다.",
        CONFIRM_REGEN_LAST_MESSAGE: "차차의 마지막 메시지를 다시 요청할래?"
    },
    EMOTION_PICKER: {
        ERROR: {
            NOTHING_SELECTED: "하나 이상의 감정을 선택해야 해!"
        },
    },

    SESSION_INFO: {
        SESSION: "세션",
        PROFILE_FORMAT: "{name}, {age}세"
    },

    LABEL: {
        NEXT: "다음",
        SEND: "보내기"
    }
}

const en = {
    SIGN_IN: {
        ERROR:{
            SESSION_ID: "You can use only roman alphabets, numbers, hyphens, and under bars, without whitespace."},
        SESSION_NAME: "Session Name",
        USER_NAME_PLACEHOLDER: "How can I call you?",
        USER_AGE_PLACEHOLDER: "How old are you?",
        START: "Start conversation!"
    },
    SHARE: {
        SAVE: "Download to CSV"
    },
    CHAT: {
        PROCESSING: "Thinking what to say... Please wait for a second!",
        INPUT_PLACEHOLDER: "Enter what you want to tell me",
        SHARE_LINK: "Share Link",
        LINK_COPIED: "Copied URL to clipboard.",
        CONFIRM_REGEN_LAST_MESSAGE: "Do you want to request Chacha to rethink this message?"
    },
    EMOTION_PICKER: {
        ERROR: {
            NOTHING_SELECTED: "You should check one or two emotions."
        },
    },

    SESSION_INFO: {
        SESSION: "Session",
        PROFILE_FORMAT: "{name}, {age}"
    },

    LABEL: {
        NEXT: "Next",
        SEND: "Send"
    }
}

export const LANGUAGE_LIST = ["한국어", "English"]

i18n.use(initReactI18next)
    .init({
        resources: {
            English: {
                translation: en
            },
            한국어: {
                translation: kr
            }
        },
        lng: '한국어',

        interpolation: {
            escapeValue: false
        }
    })

export default i18n;