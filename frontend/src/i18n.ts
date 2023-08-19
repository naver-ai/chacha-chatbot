import * as i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const kr = {
    LANGUAGE_NAME: "한국어",
    SIGN_IN: {
        ERROR:{
            SESSION_ID: "세션 아이디는 공백 없는 대소문자와 숫자, 하이픈, 언더바만 가능해."
        },
        LANG: "언어",
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
    LANGUAGE_NAME: "English",
    SIGN_IN: {
        ERROR:{
            SESSION_ID: "Only letters, numbers, hyphens, and underscores can be used. No spaces, okay?"},
        LANG: "Language",
        SESSION_NAME: "What's the session name?",
        USER_NAME_PLACEHOLDER: "What's your first name?",
        USER_AGE_PLACEHOLDER: "How old are you?",
        START: "Let's Chat!"
    },
    SHARE: {
        SAVE: "Save as CSV"
    },
    CHAT: {
        PROCESSING: "Thinking... Hang on!",
        INPUT_PLACEHOLDER: "Type what you want to say here!",
        SHARE_LINK: "Share Link",
        LINK_COPIED: "Link copied! You can paste it now.",
        CONFIRM_REGEN_LAST_MESSAGE: "Want Chacha to say that again differently?"
    },
    EMOTION_PICKER: {
        ERROR: {
            NOTHING_SELECTED: "You should check one or two emotions."
        },
    },

    SESSION_INFO: {
        SESSION: "Session",
        PROFILE_FORMAT: "{name}, {age} years old"
    },

    LABEL: {
        NEXT: "Next",
        SEND: "Send"
    }
}

export const LANGUAGE_LIST = ["kr", "en"]

i18n.use(initReactI18next)
    .init({
        resources: {
            en: {
                translation: en
            },
            kr: {
                translation: kr
            }
        },
        lng: 'kr',

        interpolation: {
            escapeValue: false
        }
    })

export default i18n;